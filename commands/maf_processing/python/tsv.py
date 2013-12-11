""" tsv - a library for processing tsv files with easy normalization
"""

import csv
import optparse
import re
import sys

__author__ = 'anorberg'


class _IdentityRange(object):

    """
    A brief utility class that pretends to be a read-only sequence or map of keys mapped to themselves.
    All keys come out as themselves.

    Sets its range based on its largest observed key.
    """

    def __init__(self, max=0):
        self._max = max

    def __getitem__(self, key):
        if isinstance(key, int):
            if key > self.max:
                self.max = key
        return key

    def __repr__(self):
        return "_Identity({0})".format(self._max)

    def __len__(self):
        return self._max

    def __iter__(self):
        return range(0, self._max)


def fixRaggedTable(inStream, outStream, dialect=csv.excel_tab):
    """
    Fixes a table with uneven row lengths. Be careful: dialect autodetection is impossible on such a table.

    The default dialect, excel_tab, is correct for most bioinformatics TSVs. Otherwise, you have to know the correct
    dialect. A ragged table prevents csv from determining the column delimiter, because the autodetector relies
    on all columns being the same width to identify candidate deilimiter characters.

    This method is to recover from an attempt to construct a TsvReader crashing due to a ragged table, since
    it relies on dialect sniffer to determine whether or not the table has a header, even if a dialect was provided.
    It reads the entire table into RAM, so it will not work with very large tables.

    Parameters:
       inStream- Open readable sequence of strings that behaves like lines of a file, such as an open file object.
       outStream- Object similar to an open-for-write file object, supporting write().
       dialect- Dialect to assume the table is in. Default is excel_tab.

    Returns:
        The number of blank cells added on the end of rows in the table to fix raggedness.
    """
    rawTableReader = csv.reader(inStream, dialect)
    parsedTable = []
    maxLen = 0
    tweaks = 0

    for record in rawTableReader:
        parsedTable.append(record)
        maxLen = max(maxLen, len(record))

    for record in parsedTable:
        while len(record) < maxLen:
            tweaks += 1
            record.append("")

    for record in parsedTable:
        outStream.write(dialect.delimiter.join(record))
        outStream.write(dialect.lineterminator)

    return tweaks


class _ParsedRecord(object):

    """
    A single row of a TSV, aware of its context.

    Attributes:
        _cells - [] of the actual records, left to right
        _headerDict - {string:int} mapping field names to column IDs
        _schemaLut - [] of int. Functions as a dense {int:int} mapping schema lookups to cell lookups.
        delim - string that is the official delimiter for the output format.
        missingfill - value to use for None values in the str output.
    """

    def __init__(self, fieldList, schemaLut, headerDict, delim="\t", missingfill=""):
        """
        Constructs a ParsedRecord.

        Parameters:
            fieldList - parsed list of the fields in the record, in their original order
            schemaLut - list representing columns in the schema. schemaLut[x] gives the index into fieldList for
                        the xth cell of the translated record.
            headerDict - key:int mapping representing all the field names to the position in fieldlist that
                         header applies to. Synonyms are represented by multiple keys mapped to the same value.
                         This should have a name for every field, not just those covered by the expected schema.
            delim - Field delimiter to use for the __str__ representation.
        """
        self._headerDict = headerDict
        self._schemaLut = schemaLut
        self._cells = fieldList
        self.delim = delim
        self.missingfill = missingfill

    def __str__(self):
        """
        Provides a string representation of the record.

        If printed, this should be a reasonable representation of this record as a row in the requested
        schema. Represents no information about the real state of the underlying record, including header or
        original cell order.

        Uses the delimter provided during construction to join fields, which can be modified via the delim attribute.
        """
        return self.delim.join((self._cells[x] if x is not None else self.missingfill for x in self._schemaLut))

    def __repr__(self):
        """
        Provides a strict Python representation of the record.

        This yields a string of a constructor call including the real cell data, the schema, the header, and the delimiter.
        """
        return "_ParsedRecord({0},{1},{2},{3},{4})".format(
            repr(self._cells), repr(self._schemaLut), repr(
                self._headerDict), repr(self.delim), repr(self.missingfill)
        )

    def __len__(self):
        """
        Returns the length of the schema, which is the iterable range of the record when indexed.

        The length of the underlying list of cells and the underlying header dictionary is not part of the calculation.
        """
        return len(self._schemaLut)

    def __nonzero__(self):
        """
        A boolean representation of this object. If the underlying cells have any nonzero data, the object is true.
        Any cell counts; it doesn't have to be a cell in the schema.
        """
        for data in self._cells:
            if data:
                return True
        return False

    def full_len(self):
        """
        Returns the real number of fields held by the record.
        """
        return len(self._cells)

    def raw_index(self, idx):
        """
        Retrieve a record by its original position in the row. Ignores schema. Not schema-safe.

        Use only as an absolute last resort. Much better is modifying the schema to include the data you
        want, or do a lookup by name (the best practice, since it results in no mysterious record indices in the code).
        """
        return self._cells[idx]

    def raw_iter(self):
        """
        Returns a generator that iterates over the original fields, rather than the schema. Not schema-safe.

        There are few cases where this is the correct strategy- use the normal __iter__ to iterate over only cells
        anticipated by the schema, which is stable to column order changes, unlike this.
        """
        return (x for x in self._cells)

    def _generateOrder(self):
        """
        Generator function that sequentially yields the fields in the schema, in schema order.
        Use __iter__ to get to this.
        """
        for idx in self._schemaLut:
            if idx is not None:
                yield self._cells[idx]
            else:
                yield None

    def __iter__(self):
        """
        Provides iteration. Provides the fields in the schema, in schema order.
        """
        return self._generateOrder()

    def __getitem__(self, idx):
        """
        Looks up a record by schema position or header.

        Integers here are treated as indexes into the schema. The record in the column expected to be in that position
        is retrieved. (If the TSV loaded was reorganized relative to the schema's expectations, the correct
        data is returned anyway. TsvReader uses header data to translate column-based lookups into the correct
        column, even if the column details change.) Slices work.

        Strings are treated as column names. The record in the column by that name is returned. If the schema
        specified synonyms, synonyms for the target column name will also work.

        If the index is an integer out of range, an IndexError will be thrown. Otherwise, if the index is not
        a column name that exists, a KeyError will be thrown. If the lookup succeeds, the value will of course
        be returned.
        """
        # type-flexibility mayhem
        try:
            cix = self._schemaLut[idx]
            if cix is None:
                return None
            return self._cells[cix]
        except TypeError:
            # maaaybe it's a slice, and cells[cix] failed
            try:
                cixes = self._schemaLut[idx.start:idx.stop:idx.step]
                ret = []
                for x in cixes:
                    if x is None:
                        ret.append(None)
                    else:
                        ret.append(self._cells[x])
                return ret
            except (AttributeError, TypeError):
                # a stringlike thing, then?
                cix = self._headerDict[str(idx)]
                if cix is None:
                    return None
                return self._cells[cix]
        # and if all those fail, throw it

    def __eq__(self, other):
        """
        Provides deep equality.
        """
        if not isinstance(other, self.__class__):
            return False
        return (self._cells == other.cells) and (self._schemaLut == other.schemaLut) and (self.delim == other.delim)


class AmbiguousSchemaError(Exception):

    def __init__(self, msg):
        super(AmbiguousSchemaError, self).__init__(msg)
        self.value = msg

    def __repr__(self):
        return "AmbiguousSchemaError(" + repr(self.value) + ")"

    def __str__(self):
        return "The schema was ambiguous: " + str(self.value)


class TsvReader:

    """
    An iterator class that reads a TSV file and yields expressive records set to fit an expected schema.

    If you don't want the fixed schema behavior, use the "csv" module instead.

    Attributes:
        header - a {string:int} mapping header names (and synonyms) to raw column indexes
        fileHeader - the [] defining the actual header on the file, which is a range of int if headerless
        schemaMap - a [] representing the original requested schema as a dense mapping of int to int (schema loc vs real loc)
        _csvSrc - a csv.Reader we use as a backing parser
        missingfill - what to fill in missing columns with
    """

    def __init__(self, sourceFile, schema, overrideHeader=None, dialect=csv.excel_tab, missingfill=""):
        """
        Constructs a TsvReader.

        Parameters:
            sourceFile - file to read. Must be an open, readable file that supports backwards seeking.
            schema - Defines the expected TSV format. If the TSV is not in that format, virtually reorder columns
                     to fake it.
                     A sequence of string represents the expected headers in the expected order. Standard operations
                     on records from this table will come from a table with that schema, even if columns need to
                     be reordered or duplicated. (Missing columns yield None.)
                     Any element in this sequence can be replaced with a sequence of strings. All strings in
                     such a subsequence are treated as though they are synonyms: that position in the record
                     (when indexed by number) will refer to any column by any of those names (if this defines
                     multiple columns, this initializer will throw an AmbiguousSchemaError), so similar TSVs
                     with equivalent data but different naming conventions can be used with no code changes.
                     Similarly, the elements of a synonym list are made to refer to the same column during
                     lookup by name, so any synonym will get the column actually in the table if using
                     strings to index the records, again insulating code from variations in the TSV schema
                     beyond this point.
            overrideHeaeder - Forces the header for the document. If the document has a header, this overrides it.
                              If the document does not have a header, this provides it.
                              If overrideHeader is None, only the original header is used. (If there is no
                              header, ints from 0 to the length of a row minus 1 are used as the header.)
                              Otherwise, overrideHeader is a sequence of str used as headers.
            dialect - A csv Dialect, from the csv library. If you don't know the dialect of your file, and you
                      don't think it's Excel's TSV standard (excel_tab, the default), use csv.Sniffer to
                      make a best guess at it. Please see csv's docs for more details.
            missingfill - the string to fill missing columns specified in the schema with. Defaults to "".
        """

        mark = sourceFile.tell()
        # some of our files have ludicrously long lines, and we need at least 3
        sample = sourceFile.read(32767)
        hasHeader = csv.Sniffer().has_header(sample)
        sourceFile.seek(mark)  # reset to original position
        self._csvSrc = csv.reader(sourceFile, dialect=dialect)
        self.missingfill = missingfill

        if hasHeader:
            self.fileHeader = self._csvSrc.next()
        else:
            self.fileHeader = _IdentityRange()

        if overrideHeader:
            self.fileHeader = overrideHeader  # ha ha, never mind!
            # we still had to pull the real header off, though

        self.header = {}
        self.schemaMap = []
        for idx in range(0, len(self.fileHeader)):
            self.header[self.fileHeader[idx]] = idx

        for schemite in schema:
            if isinstance(schemite, str):
                # single-cast lookup
                try:
                    loc = self.header[schemite]
                except KeyError:
                    loc = None
                self.schemaMap.append(loc)
            else:
                # multicast lookup
                # TODO: fix this logic for headerless reordering
                loc = None
                for name in schemite:
                    if name in self.header:
                        if loc is None:
                            loc = self.header[name]
                        else:
                            raise AmbiguousSchemaError("Two entries in a schema synonym list were both found." +
                                                       "The second one is \"" + name + "\".")
                # now we know the location, or know it's not there
                for name in schemite:
                    # this will result in one redundant assignment
                    self.header[name] = loc
                self.schemaMap.append(loc)

    def next(self):
        """
        Returns a representation of the next record pretending to fit the schema for the TSV.

        Raises StopIteration once it is out of data.
        """
        line = self._csvSrc.next()  # if this throws a StopIteration, fantastic
        return _ParsedRecord(line, self.schemaMap, self.header, self._csvSrc.dialect.delimiter, self.missingfill)

    def __iter__(self):
        """
        Returns an iterable view of the loaded TSV. This class is one, so it returns itself.
        """
        return self

usagenotes = """
Either fixedschema or regex must be specified. There is no default,
since a destination table format must be specified, and there is no way
to specify a sensible default for such.

The argument to regex is a single Python regular expression. Columns with
headers that match that regular expression will be preserved in the output,
in the same order they were in the input. Regular expressions are in the
regex format of the Python language.

The argument to fixedschema is a schema list. Provide the names of the
columns you would like, in order, case-sensitive, separated by semicolons. If
those columns may have different names in the input file, list those possible
names separated by commas immediately after the name you wish the column
to be output under. For example:

one;two;three,3,twee;four

will output a table with columns named "one", "two", "three", and "four", and
the content for column "three" could come from a column by any of the names
"three", "3", or "twee". If any two (or more) of these names are both actual
column names, tsv.py will crash with an AmbiguousSchemaError. If a column
is missing, it will be filled in the output with the string specified from
the --missingfill option, which defaults to the blank string. missingfill
can only apply to fixed schema mode.

If both fixedschema and regex are specified, the regex match is added to the
end of the fixed schema. This may duplicate columns.

This version of the code has no way to escape literal "," or ";" in header
names desired for a schema. A later version may try to address this.
"""


def main(argv):
    """
    Acts as an entry point if this module is run as a script from the CLI. Functions as a TSV rearranger.
    """
    parser = optparse.OptionParser(
        usage="usage: %prog [options] inputFile outputFile",
        epilog=usagenotes)
    parser.add_option(
        "-s", "--fixedschema", dest="schema", help="Create a table with a specific SCHEMA.",
        metavar="SCHEMA", default=None, action="store", type="string")
    parser.add_option(
        "-r", "--regex", dest="regex", help="Create a table from columns with names that fit a REGEX.",
        metavar="REGEX", default=None, action="store", type="string")
    parser.add_option(
        "-x", "--removeheader", dest="removeheader", help="Do not print a header line in the output.",
        default=False, action="store_true")
    parser.add_option(
        "-m", "--missingfill", dest="missingfill", help="Fill missing columns (in fixedschema mode) with STRING",
        metavar="STRING", default="", action="store", type="string")

    (flags, args) = parser.parse_args(argv[1:])

    if len(args) != 2 or (not flags.schema and not flags.regex):
        print "Incorrect number of arguments or no transformation specified."
        parser.print_help()
        return

    input = open(args[0], "r")
    output = open(args[1], "w")

    schema = []
    header = []

    if flags.schema:
        things = flags.schema.split(";")
        for item in things:
            synonyms = item.split(",")
            header.append(synonyms[0].strip())
            schema.append([name.strip() for name in synonyms])

    if flags.regex:
        csv_view = csv.reader(input, csv.excel_tab)
        input_header = csv_view.next()
        del csv_view
        input.close()
        del input
        input = open(args[0], "r")
        pattern = re.compile(flags.regex)
        for name in input_header:
            if pattern.search(name):
                header.append(name)
                schema.append(name)

    if not flags.removeheader:
        output.write("\t".join(header))
        output.write("\n")

    for recordline in TsvReader(input, schema, missingfill=flags.missingfill):
        output.write(str(recordline))
        output.write("\n")

    output.flush()
    output.close()
    return


if __name__ == "__main__":
    main(sys.argv)
