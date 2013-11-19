#gidget style guide

## python
gidget is primarily written in python.  Here are some simple guidelines for friendly collaborative coding:


### python interpreter
Not all files need to start with a 'hashbang' (`#!`), but for those that do, use `#!/usr/bin/env python`

### indentation
- indentation should be **4 spaces**
- indentation should use spaces, **not** tabs
    
### settings for vim
You may need to turn on modeline scanning in your vimrc file.  For example:

```
cat ~/.vimrc:

set modelines=5
```    

Then, within the first five lines of a python code file, use a _commented_ line to set some vim variables:

```
#!/usr/bin/env python

[...]
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

```

### settings for emacs
The python mode in modern emacs probably does the right thing by default, but we can give it some hints as well for consistency.  (Also, some other editors may understand this information as well.)  Near the top of a python code file, use a _commented_ line to set python editing behavior in emacs:

```
#!/usr/bin/env python

[...]
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

```

### putting it together
Both emacs and vim file settings can coexist.  The following code should be used as a template for new _exectuable_ python files in this project:

```
#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

```

Other python files which are _not_ executable, and do not need the interpreter's 'hashbang' line, should start like this:

```
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

```

### hints for using other editors

#### Sublime Text


Add this to your Preferences -> Settings - Users
```
{
	"tab_size": 4,
    "translate_tabs_to_spaces": true
}
```

## line endings

When working with developers who use different operating systems, line endings can be an issue. So, the github respository has been configured to 1) store files with unix-style normalized line endings and 2) check out files with your own OS's native line-ending style. In short, you shouldn't have to worry about this issue.


Happy coding!

