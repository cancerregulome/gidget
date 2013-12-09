#!/usr/bin/python 

# This is a version of DCC Snapshot 2.0 that runs under Python 2.4. 
# It no longer prints out the handy help text specified by 
# later-supported epilog param of optparse. Since this is meant to 
# run in an automated fashion and is quite verbose with its error  
# messages, I feel this change is worthwhile.

# Last revision: February 22nd, 2011 by Tom Robinson

import os
import sys
import re
import shutil
import stat
import optparse
import ConfigParser
import logging

log = logging.getLogger("dcc_snapshot")

class IsFileError(IOError):
    def __init__ (self, boguspath):
        self.fault = boguspath
    def __str__ (self):
        return "IsFileError implies that this \
is a file when I wanted a directory: " + self.fault
    def __repr__(self):
        return "IsFileError(" + repr(self.fault) +")"

class DestinationClobberError(IOError):
    def __init__ (self, boguspath):
        self.fault = boguspath
    def __str__ (self):
        return "DestinationClobberError implies that this is probably not\
 something you wanted me to delete: " + self.fault
    def __repr__(self):
        return "DestinationClobberError(" + repr(self.fault) +")"

class PluginManager(object):
    def __init__ (self, plugcfg = None):
        self.plugins = set()
        self.plugcfg = plugcfg
    
    def directory_linked(self, src, dest, isNew):
        for plugin in self.plugins:
            try:
                plugin.directory_linked(src, dest, isNew)
            except AttributeError:
                log.debug(str(plugin) + " has no directory_linked")

    def done_linking_directories(self):
        for plugin in self.plugins:
            try:
                plugin.done_linking_directories()
            except (AttributeError):
                log.debug("That plugin doesn't care if we're done")

    def sweeping(self, old, new):
        for plugin in self.plugins:
            try:
                plugin.sweeping(old, new)
            except AttributeError:
                log.debug(str(plugin) + " has no sweeping")

    def done_sweeping(self):
        for plugin in self.plugins:
            try:
                plugin.done_sweeping()
            except (AttributeError):
                log.debug("That plugin doesn't care if we're done")

    def directory_complete(self, path):
        for plugin in self.plugins:
            try:
                plugin.directory_complete(path)
            except (AttributeError):
                log.debug("That plugin has no directory_complete")

    def add_plugin_path(self, path):
        path = path.strip()
        if len(path) == 0:
            log.warning("add_plugin_path called with blank path")
            return
        sys.path.insert(0, path)
        
    def add_plugin(self, candidate_module):
        candidate_module = candidate_module.strip()
        if len(candidate_module) == 0:
            log.warning("add_plugin called with blank path")
            return
        try:
            plugin_mod = __import__(candidate_module)
            if plugin_mod not in plugins:
                plugins.add(plugin_mod)
                plugin_mod.initialize_plugin(self.plugcfg)
        except ImportError:
            if(candidate_module.endswith((".py", ".PY"))):
                log.info("Removing trailing .py from plugin name: " + candidate_module)
                self.add_plugin(candidate_module[:-3])
                return
            log.error("Could not load requested plugin module at all: "
                    + candidate_module)
        except AttributeError:
            log.debug("Plugin had no initialize_plugin, probably")
        #let TypeError be an error

level_regex = re.compile(r"(?P<key>.*\.Level_\d+\.\d+\.)"
                        r"(?P<revision>\d+)\.(?P<build>\d+)$"
                        )
magetab_regex = re.compile(r"(?P<key>.*\.mage-tab\.\d+\.)"
                        r"(?P<revision>\d+)\.(?P<build>\d+)$"
                        )
plugs = PluginManager()

def max_shove(dic, key, value):
    """Update a key in the dictionary if the previous value was lower.
    
    dic -- dictionary to insert into
    key -- key to query
    value -- proposed new value
    
    The dictionary is queried for the key. If the key is not in the
    dictionary at all, it is inserted with the specified value.
    If it is in the dictionary, its corresponding value is compared
    to the provided value. If the new value is higher, the value in
    the dictionary is updated and the function returns True (same
    as if there is no key); if it is not, the dictionary is unchanged
    and the function returns False."""
    if (key not in dic) or value > dic[key]:
        dic[key] = value
        return True
    return False

def slay_the_weaker(dic, key, value):
    """Delete the less-up-to-date directory by the same name, if any.
    
    Parameters:
    dic -- Dictionary of absolute paths minus version numbers to
            version numbers
    key -- String representing the absolute path minus version number
            to check against
    value -- Version number of candidate for new maximum or deletion
    
    If the key does not exist in the table, it is created and this
    function returns False. If the key does exist, values are compared.
    The directory corresponding to the lower value is recursively
    deleted, and the higher value is inserted into the table. If the
    values are equal, the function simply returns, although this case
    shouldn't happen in the context of how the function was initially
    written.
    
    Calls on-sweep plugins before the sweep."""
    
    if not(key in dic):
        dic[key] = value
        log.debug("No competitor for directory " + key +"."+str(value))
        return False
    log.debug("Comparing two directories: " + key + " of " + str(dic[key]) +
              " and " + str(value))
    if value > dic[key]:
        low = key + str(dic[key][0]) + "." + str(dic[key][1])
        high = key + str(value[0]) + "." + str(value[1])
        dic[key] = value
    elif value == dic[key]:
        log.error("slay_the_weaker found a clone: " +key+"."+str(value))
        return False
    else:
        low = key + str(value[0]) + "." + str(value[1])
        high = key + str(dic[key][0]) + "." + str(dic[key][1])
    log.info("Sweeping out of date directory: " + low)
    plugs.sweeping(low, high)
    shutil.rmtree(low)
    return True

def dont_kill_the_repository(path, recursive = True):
    """Throw an exception if the specified path is not safe to write.
    
    Parameters:
    path -- Path to check for safety
    recursive -- Whether or not to check subdirectories for safety,
                 as opposed to blindly assuming it
    Throws:
        A DestinationClobberError if it looks like the specified directory
        is anything other than a snapshot directory.
    A snapshot directory should contain only symlinks and subdirectories
    that are themselves valid snapshot directories. Anything else
    might be real data and is not safe to blindly overwrite with this
    specific tool, which should only be writing into a new directory or
    overwriting a previous snapshot directory because its write behavior
    is highly destructive."""
    log.debug("Making sure destroying " + path + " isn't ruinous")
    if not os.path.isdir(path):
        log.critical(path + ", slated for destruction, is not a directory. " + 
                    "abort in dont_kill_the_repository")
        raise DestinationClobberError(path)
    for name in os.listdir(path):
        checkpath = os.path.join(path, name)
        if not os.path.islink(checkpath):
            if os.path.isdir(checkpath):
                if recursive:
                    dont_kill_the_repository(checkpath)
            else:
                log.critical(name + " is a real file in " +
                        "condemned directory " + path + ". abort in " +
                        "dont_kill_the_repository")
                raise DestinationClobberError(checkpath)
    log.debug("dont_kill_the_repository says " + path + " is okay")
    return True

def recursive_symlinkify(src, dest):
    """Create a recursive symlink copy in dest of src.
    
    Parameters:
    src -- Path to make a shallow symlink copy of
    dest -- Where to put it
    If dest is already populated, it is verified to be safe to overwrite
    using a recursive call to dont_kill_the_repository. It is then
    deleted and simply rewritten; no attempt is made to "update" such
    a directory. A directory is safe to overwrite if and only if it
    contains only symlinks and subdirectories that are, by the same
    rule, safe to overwrite."""
    log.debug("recursively shadowing " + src + " into " + dest)
    if not os.path.isdir(src):
        log.critical("recursive_symlinkify can't recurse into " +
                    src + " because it isn't a directory. abort")
        raise IsFileError(src)
    if os.path.exists(dest):
        if os.path.isfile(dest):
            log.critical(dest + " exists as a file and " +
                    "recursive_symlinkify is trying to write a " +
                    "directory over it, which is probably bad. abort")
            raise DestinationClobberError(dest)
        if os.path.isdir(dest):
            dont_kill_the_repository(dest)
            shutil.rmtree(dest)
        else:
            log.critical(dest+" exists, but isn't a file or directory" +
                    " and recursive_symlinkify has no idea what to do" +
                    " with that kind of thing. abort")
            raise IOError
    os.mkdir(dest)
    for name in os.listdir(src):
        srcpath = os.path.join(src, name)
        destpath = os.path.join(dest, name)
        if os.path.isdir(srcpath):
            recursive_symlinkify(srcpath, destpath)
        elif os.path.isfile(srcpath):
            log.debug("writing symlink: " + srcpath + "  ==>  " +
                        destpath)
            os.symlink(srcpath, destpath)

def sweep(path):
    """Delete everything but the most up-to-date revisions."""
    log.info("Cleaning up old directories in " + path)
    dont_kill_the_repository(path, False) #sweep is called depth-first
                        #so setting recurse to true will cause d^2 perf
    matchtable = {}
    for entry in os.listdir(path):
        fullpath = os.path.join(path, entry)
        if not os.path.isdir(fullpath):
            continue
        match = level_regex.match(entry)
        if match is None:
            match = magetab_regex.match(entry)
        if match is None:
            log.warning("Non-snapshot directory found in sweep target: "
                    + fullpath)
            continue
        #now it's one of the types
        myrevision = (int(match.group("revision")),
                      int(match.group("build")))
        slay_the_weaker(matchtable, 
                        os.path.join(path, match.group("key")),
                        myrevision)

def recursive_latest(src, dest):
    """Create a snapshot of the latest data in the directory.
    
    Recurses on all subdirectories. Latest is defined as, for each
    major version of a MAGE_TAB directory, the highest-numbered minor
    version; for a leve_n directory, for each major.minor version,
    the highest-numbered revision. (Assumes major.minor.revis.build)"""
    
    #destination directory-making postponed: only happens if
    #there's anything in this entire tree that we care about

    print "         in recursive_latest ", src, dest
    
    matchtable = {}
    log.info("Scanning " + src)
    for entry in os.listdir(src):
        srcpath = os.path.join(src, entry)
        destpath = os.path.join(dest, entry)
        if os.path.isfile(srcpath):
            continue
        log.debug("at " + src + " processing " + entry)
        match = level_regex.match(entry)
        if match is None:
            match = magetab_regex.match(entry)
        #now if it's none, it's neither type
        if match is not None:
            log.debug("Comparing/inserting " + entry)
            myrevision = (int(match.group("revision")), 
                          int(match.group("build")))
            max_shove(matchtable, match.group("key"), myrevision)
        else:
            recursive_latest(srcpath, destpath)
            
    #matchtable now contains the highest edition for each
    log.debug("table of " + src + ": " + str(matchtable))
    if len(matchtable):
        log.info("Found objects in " + src + ", mirroring into " + dest)
        if not os.path.exists(dest):
            os.makedirs(dest)
        elif os.path.isfile(dest):
            raise IsFileError(dest)
    for primary, edition in matchtable.iteritems():
        name = primary + str(edition[0]) + "." + str(edition[1])
        srcpath = os.path.join(src, name)
        destpath = os.path.join(dest, name)
        is_new = not os.path.exists(destpath)
        recursive_symlinkify(os.path.abspath(srcpath), destpath)
        plugs.directory_linked(srcpath, destpath, is_new)
    
    if len(matchtable):
        sweep(dest)
        plugs.directory_complete(dest)
    
    return len(matchtable)

def recursive_chmod(path, value):
    """Recursively sets directory permissions."""
    for root, dirs, files in os.walk(path):
        for directory in dirs:
            log.debug("Chmodding " + root + "/" + directory)
            try:
                os.chmod(os.path.join(root, directory), value)
            except OSError:
                log.error("Couldn't chmod"+os.path.join(root, directory) 
                      + "-- moving on")

if __name__ == "__main__":
    detailtext = """Creates a snapshot of the latest data in a dcc tree.
Data is identified as a directory ending in Level_[n].[version]
or mage-tab.[version], where a Level directory is expected
to have a four-part version and a mage-tab expected to have
a three-part version.

The "latest" data is the highest-revision Level data for each
uniquely-named level_* root and each major.minor version, and
the highest-minor-version mage-tab data for each uniquely-named
mage-tab root.

The snapshot is a clone of the directory structure
stripped down to directories that contain data,
and data directories themselves only have the latest, which
is a symlink to the real data directory.

SRC: the directory to make a snapshot of.
DEST: the directory to create the snapshot in. If the name does
not contain "snapshot" somewhere on the path, it will be
rejected unless the -f/--force option is used.
CONFIGFILE: Instead of using SRC/DEST, a configuration file can
be specified instead. Using a configuration file does not imply
-f, so if the config file specifies a destination without
the text "snapshot" in its path, -f or --force must be used."""
    parser = optparse.OptionParser(
                                usage="%prog [options] SRC DEST\n"
                                "\t%prog [options] CONFIGFILE",
                                version="%prog 2.1")
    parser.add_option("-l", "--logfile", dest="logfile", default=None,
            help="Specify a log file- default is console")
    parser.add_option("-v", "--verbosity", dest="verbosity",
            default="INFO", type="string",
            help="Logging noise level; chooose from "
                 "ERROR, WARN, INFO, or DEBUG. "
                 "Please be aware that DEBUG will produce "
                 "extremely large logs, as every symlink is recorded. "
                 "Defualt is INFO.")
    parser.add_option("-o", "--override", dest="override",
            action="store_true", default=False,
            help="Override a specified configuration file. "
                 "Can only be used when a configuration file is used. "
                 "Causes -v and -l settings to override settings in "
                 "specified configuration file.")
    parser.add_option("-f", "--force", dest="force", 
            action="store_true", default=False,
            help="Suppress check that dest contains 'snapshot'")
    parser.add_option("-d", "--plugin-directories", dest="plug_path",
            default=None, help="Path to search for plugins")
    parser.add_option("-p", "--plugins", dest="plugins", default=None,
            help="Plugin scripts to use after copies/before removals")
    parser.add_option("-c", "--plugcfg", dest="plugcfg", default=None,
            help="Configuration file for all plugins (it's up to plugins to use separate sections)")
            
    flags, args = parser.parse_args()
    src = dest = config = None
    if len(args) == 0:
        parser.error("No configuration file or SRC/DEST specified")
    elif len(args)==1:
        # config mode
        config = ConfigParser.SafeConfigParser(
                {
                    "verbosity":"INFO",
                    "logfile":None,
                    "plugins":None,
                    "plugin-directories":None,
                    "plugcfg":None
                }
            )
        config.read(args[0])
        try:
            src = config.get("dcc-snapshot", "src")
            dest = config.get("dcc-snapshot", "dest")
        except IOError:
            if src is None:
                parser.error("Configuration file did not contain 'src'")
            if dest is None:
                parser.error("Configuration file did not contain 'dest'")
    elif len(args) == 2:
        #src dest mode
        src = args[0]
        dest = args[1]
    else:
        parser.error("Too many arguments.")
    
    if not flags.force:
        if dest.find("snapshot") == -1:
            parser.error("Destination argument " + dest +
                         " may not be a snapshot directory (failed check"
                         " for 'snapshot' in the name). Specify a "
                         "snapshot directory instead, or use the -f "
                         "option to override this check.")
    
    logger = logging.getLogger("dcc_snapshot")
    handler = vosity = None
    if config is None or (flags.override and flags.logfile is not None):
        if flags.logfile is None:
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(flags.logfile)
    else:
        lfile = config.get("dcc-snapshot", "logfile")
        if lfile is None:
            lfile = flags.logfile
            
        if lfile is None or lfile == "":
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(lfile)
        
    formatter = logging.Formatter("%(asctime)s - %(name)s - "
                                         "%(levelname)s - %(message)s")
    vosity = flags.verbosity.upper()
    if config is not None and not flags.override:
        temp = config.get("dcc-snapshot", "verbosity")
        if temp is not None:
            vosity = temp

    if vosity == "CRITICAL":
        handler.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)
    elif vosity == "ERROR":
        handler.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif vosity == "WARNING" or vosity == "WARN":
        handler.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif vosity == "INFO" :
        handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif vosity == "DEBUG":
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        parser.error("verbosity: Invalid value")
    logger.addHandler(handler)
    logger.debug("Logger initialized.")

    if flags.override:
        if flags.plugcfg:
            plugs.plugcfg = ConfigParser.SafeConfigParser()
            plugs.plugcfg.read(flags.plugcfg)
        elif config:
            plugcfg = config.get("dcc-snapshot", "plugcfg")
            if plugcfg:
                plugs.plugcfg = ConfigParser.SafeConfigParser()
                plugs.plugcfg.read(plugcfg)
    else:
        if config:
            plugcfg = config.get("dcc-snapshot", "plugcfg")
            if plugcfg:
                plugs.plugcfg = ConfigParser.SafeConfigParser()
                plugs.plugcfg.read(plugcfg)
        elif flags.plugcfg:
            plugs.plugcfg = ConfigParser.SafeConfigParser()
            plugs.plugcfg.read(flags.plugcfg)


    if flags.plug_path:
        for path in flags.plug_path.split(";"):
            plugs.add_plugin_path(path)

    if config:
        paths = config.get("dcc-snapshot", "plugin-directories")
        if paths is not None:
            for path in paths.split(";"):
                plugs.add_plugin_path(path)

    if flags.plugins:
        for plug in flags.plugins.split(";"):
            plugs.add_plugin(plug)

    if config:
        plug_group = config.get("dcc-snapshot", "plugins")
        if plug_group is not None:
            for plug in plug_group.split(";"):
                plugs.add_plugin(plug)

    recursive_latest(src, dest)
    plugs.done_linking_directories()
    plugs.done_sweeping()
    ## this seems to be causing problems ??? SMR 6-dec-12 
    ## recursive_chmod(dest, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) #world-writable: 777

