# qmake2cmake

This repository contains Python scripts to convert QMake projects to
CMake projects.

## Goals

The qmake2cmake tool creates a `CMakeLists.txt` that covers the most common
attributes of the converted `.pro` file.  The generated CMake project can be
used as baseline and will most likely need manual adjustments.

QMake constructs that cannot be converted end up in the CMake project as
comment.

## Non-goals

The following QMake constructs are not converted:
- `TEMPLATE = aux` projects
- custom `.prf` files
- extra compilers
- extra targets
- installation rules

# Requirements

* [Python 3.7](https://www.python.org/downloads/),
* `pipenv` or `pip` to manage the modules.

## Python modules

Since Python has many ways of handling projects, you have a couple of options to
install the dependencies of the scripts:

### Using `pipenv`

The dependencies are specified on the `Pipfile`, so you just need to run
`pipenv install` and that will automatically create a virtual environment
that you can activate with a `pipenv shell`.

### Using `pip`

It's highly recommended to use a [virtual
environment](https://docs.python.org/3/library/venv.html) to avoid
conflicts with other packages that are already installed.

* Create an environment: `python3 -m venv env --prompt qmake2cmake`,
* Activate the environment: `source env/bin/activate`
  (on Windows: `env\Scripts\activate.bat`)
* Install the requirements: `pip install -r requirements.txt`

If the `pip install` command above doesn't work, try:

```
python3.7 -m pip install -r requirements.txt
```

# Usage

The following call converts a single QMake project file to CMake:
```
qmake2cmake ~/projects/myapp/myapp.pro --min-qt-version 6.3
```

It's necessary to specify a minimum Qt version the project is supposed
to be built with. Use the `--min-qt-version` option or the
environment variable `QMAKE2CMAKE_MIN_QT_VERSION`.

By default, a `CMakeLists.txt` is placed next to the `.pro` file.

To generate `CMakeLists.txt` in a different location, use the `-o` option:
```
qmake2cmake ~/projects/myapp/myapp.pro --min-qt-version 6.3 -o ~/projects/myapp-converted/CMakeLists.txt
```

To convert a whole project tree, pass the project directory to `run_qmake2cmake`:
```
run_qmake2cmake ~/projects/myapp --min-qt-version 6.3
```

# Contributing to the scripts

You can verify if the styling of a script is compliant with PEP8, with a couple of exceptions:

Install [flake8](http://flake8.pycqa.org/en/latest/) (`pip install flake8`) and run it
on all python source files:

```
make flake8
```

You can also modify the file with an automatic formatter,
like [black](https://black.readthedocs.io/en/stable/) (`pip install black`),
and execute it:

```
make format
```
