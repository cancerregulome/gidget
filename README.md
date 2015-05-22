gidget
======

## TCGA Feature Matrix Pipeline

The gidget project bundles many scripts used in the creation of the TCGA feature matrix type.  Many bioinformatics references as well as input data files (from the TCGA DCC and otherwise) are combined through the many sub-pipelines that compose the overall gidget pipeline.  On a properly configured system which contains all required supporting reference and datafiles as well as the (separate) pairwise analysis pipeline, the entire feature matrix process can be run with one top-level gidget command; alternatively the component sub-pipelines can be run with their own top-level gidget commands.  Some additional command information can be found under pipelines/README.md.

Note: this is a beta project currently under development.

## installation dependencies:

  * SciPy and NumPy (http://docs.scipy.org/doc/numpy/user/install.html)
```bash
  $ git clone https://github.com/numpy/numpy.git
  $ git clone https://github.com/scipy/scipy.git
```

  * Both NumPy and SciPy are built as follows
```bash
  $ python setup.py build
  $ python setup.py install
```

  * RuntimeError: Running cythonize failed!
```bash
  $ [sudo] easy_install cython
```

## Python Version 

The python scripts in this project require Python 2.7 (and not Python 3) to run. If you are have issues with the python version and imported modules, the first thing to look at is verifying that a Python 2.7 executable is the first "python" that will be found when the system looks at the `$PATH` environment variable. This means you might have to change the order or the directories in `$PATH` or preprend a directory containing Python 2.7. If you are unfamiliar with how the `$PATH` variable works, some info can be found [here](http://www.linfo.org/path_env_var.html).
