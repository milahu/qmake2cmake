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

# Installation

You can install the package directly via `pip install qmake2cmake`.

In case you are developing a new feature or want to install the latest
repository version, do an editable build by running `pip install -e .`

# Usage

After installing the `qmake2cmake` package, two scripts will be
available in your bin/ directory of your Python environment:
`qmake2cmake` and `qmake2cmake_all`.

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

To convert a whole project tree, pass the project directory to `qmake2cmake_all`:
```
qmake2cmake_all ~/projects/myapp --min-qt-version 6.3
```

# Contributing

The main source code repository is hosted at
[codereview.qt-project.org](https://codereview.qt-project.org/q/project:qt/qmake2cmake).

See the [Qt Contribution Guidelines](https://wiki.qt.io/Qt_Contribution_Guidelines)
page, [Setting up Gerrit](https://wiki.qt.io/Setting_up_Gerrit) and
[Gerrit Introduction](https://wiki.qt.io/Gerrit_Introduction) for more
details about how to upload patches for review.

## Code style and tests

You can run the linter (`mypy`), code-style checkers (`flake8`, `black`)
and tests (`pytest`) by executing:

```
make test
```

There are also separate make targets for each of those `make mypy`, `make flake8`,
`make black_format_check`, `make pytest`.

You can auto-format the code using [black](https://black.readthedocs.io/en/stable/):

```
make format
```


# Releasing a new version

Increase the version number in `setup.cfg` according to semantic versioning 2.0.

For building and uploading `qmake2cmake` you will need the Python
modules `build` and `twine`.

Build the wheel:
```
$ python -m build
```

Upload to testpypi:
```
$ twine upload --repository testpypi dist/<wheel-name>
```

Install the uploaded wheel in a fresh venv:
```
$ python -m venv fresh && . ./fresh/bin/activate
(fresh)$ pip install -i https://testpypi.python.org/pypi qmake2cmake --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple

```

If the installation succeeded, try to convert something.
If everything is bueno, upload the wheel to production pypi.

```
$ twine upload --repository pypi dist/<wheel-name>
```

It is advisable to try out this wheel in another fresh venv.
