#!/usr/bin/env python3
#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the plugins of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

from qmake2cmake.pro2cmake import Scope, SetOperation, merge_scopes, recursive_evaluate_scope
from qmake2cmake.pro2cmake import main as convert_qmake_to_cmake # qmake2cmake
from qmake2cmake.run_pro2cmake import main as convert_qmake_to_cmake_all # qmake2cmake_all

import filecmp
import functools
import os
import pathlib
import pytest
import re
import shutil
import sys
import tempfile

from typing import Callable, Optional

debug_mode = bool(os.environ.get("DEBUG_QMAKE2CMAKE_TEST_CONVERSION"))
test_script_dir = pathlib.Path(__file__).parent.resolve()
test_data_dir = test_script_dir.joinpath("data", "conversion")

if debug_mode:
    print("running test with debug_mode=True")

def compare_expected_output_directories(actual: str, expected: str):
    dc = filecmp.dircmp(actual, expected)
    if dc.diff_files:
        print("error in snapshot test")
        print()
        print("diff:")
        print(f"- actual   {actual}")
        print(f"+ expected {expected}")
        try:
            os.system(f"diff -r -u --color=always {actual} {expected}")
        except Exception as e:
            print(f"failed to call diff: {e}")
        print()
        if debug_mode:
            e_rel = os.path.relpath(expected, os.getcwd())
            print("to update the expected files, run:")
            print(f"git rm -r {e_rel}")
            print(f"cp -r {actual} {e_rel}")
            print(f"git add {e_rel}")
            print(f"git status")
            print(f"git commit")
        else:
            print("to keep the actual files, run:")
            print("  DEBUG_QMAKE2CMAKE_TEST_CONVERSION=1 pytest")
    assert(dc.diff_files == [])


def convert(
        base_name: str,
        *,
        min_qt_version: str = "6.2.0",
        recursive: bool = False,
        after_conversion_hook: Optional[Callable[[str], None]] = None
    ):
    '''
    Converts {base_name}.pro to CMake in a temporary directory.

    The optional after_conversion_hook is a function that takes the temporary directory as
    parameter.  It is called after the conversion.
    '''
    pro_file_name = str(base_name) + ".pro"
    pro_file_path = test_data_dir.joinpath(pro_file_name)
    assert(pro_file_path.exists())

    with tempfile.TemporaryDirectory(prefix="testqmake2cmake") as tmp_dir: # auto delete

        convert_fn = convert_qmake_to_cmake
        if recursive:
            convert_fn = convert_qmake_to_cmake_all

        tmp_dir_path = pathlib.Path(tmp_dir)
        output_file_path = tmp_dir_path.joinpath("CMakeLists.txt")

        convert_args = []
        convert_args += ["--min-qt-version", min_qt_version]
        if recursive:
            convert_args += ["--output-dir", tmp_dir]
            convert_args += ["--main-file", pro_file_path.name]
            convert_args += [pro_file_path.parent]
        else:
            # TODO also use --output-dir. not tested ...
            convert_args += ["--output-file", output_file_path]
            convert_args += [pro_file_path]

        # argparse expects list of strings
        convert_args = list(map(str, convert_args))

        convert_fn(convert_args)

        if debug_mode:
            # TODO keep files only on failed test
            # tempdirs on linux: /run/user/$UID/testqmake2cmake*
            tmp_dir_persistent = tempfile.mkdtemp(prefix="testqmake2cmake") # manual delete
            shutil.copytree(tmp_dir, tmp_dir_persistent, dirs_exist_ok=True)
            print(f"test_conversion.py: keeping temporary files: {tmp_dir_persistent}")

        f = open(output_file_path, "r")
        assert(f)
        content = f.read()
        assert(content)

        if after_conversion_hook:
            after_conversion_hook(actual=tmp_dir)

        return content


def convert_and_compare_expected_output(
        pro_base_name: str,
        rel_expected_output_dir: str,
        recursive: bool = False,
    ):
    expected = str(test_data_dir.joinpath(rel_expected_output_dir))
    def after_conversion_hook(actual: str):
        compare_expected_output_directories(expected, actual)
    convert(
        pro_base_name,
        after_conversion_hook=after_conversion_hook,
        recursive=recursive
    )


def test_qt_modules():
    '''Test the conversion of QT assignments to find_package calls.'''
    output = convert("required_qt_modules")
    find_package_lines = []
    for line in output.split("\n"):
        if "find_package(" in line:
            find_package_lines.append(line.strip())
    assert(["find_package(QT NAMES Qt5 Qt6 REQUIRED)",
            "find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Network Widgets)"] == find_package_lines)

    output = convert("optional_qt_modules")
    find_package_lines = []
    for line in output.split("\n"):
        if "find_package(" in line:
            find_package_lines.append(line.strip())
    assert(["find_package(QT NAMES Qt5 Qt6 REQUIRED)",
            "find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Network Widgets)",
            "find_package(Qt${QT_VERSION_MAJOR} OPTIONAL_COMPONENTS OpenGL)"] == find_package_lines)

def test_qt_version_check():
    '''Test the conversion of QT_VERSION checks.'''
    output = convert("qt_version_check")
    interesting_lines = []
    for line in output.split("\n"):
        if line.startswith("if(") and "QT_VERSION" in line:
            interesting_lines.append(line.strip())
    assert(["if(( ( (QT_VERSION_MAJOR GREATER 5) ) AND (QT_VERSION_MINOR LESS 1) ) AND (QT_VERSION_PATCH EQUAL 0))", "if(( ( (QT_VERSION VERSION_GREATER 6.6.5) ) AND (QT_VERSION VERSION_LESS 6.6.7) ) AND (QT_VERSION VERSION_EQUAL 6.6.6))"] == interesting_lines)


def test_subdirs():
    '''Test conversion of a TEMPLATE=subdirs project.'''
    convert_and_compare_expected_output("subdirs/subdirs", "subdirs/expected", recursive=True)


def test_common_project_types__app():
    output = convert("app")
    assert(r"""
qt_add_executable(app WIN32 MACOSX_BUNDLE)
target_sources(app PRIVATE
    main.cpp
)
""" in output)

def test_common_project_types__app_cmdline():
    output = convert("app_cmdline")
    assert(r"""
qt_add_executable(myapp)
target_sources(myapp PRIVATE
    main.cpp
)
""" in output)

def test_common_project_types__app_console():
    output = convert("app_console")
    assert(r"""
qt_add_executable(myapp MACOSX_BUNDLE)
target_sources(myapp PRIVATE
    main.cpp
)
""" in output)

def test_common_project_types__app_nonbundle():
    output = convert("app_nonbundle")
    assert(r"""
qt_add_executable(myapp WIN32)
target_sources(myapp PRIVATE
    main.cpp
)
""" in output)

def test_common_project_types__lib_shared():
    output = convert("lib_shared")
    assert(r"""
qt_add_library(lib_shared)
target_sources(lib_shared PRIVATE
    lib.cpp
)
""" in output)

def test_common_project_types__lib_static():
    output = convert("lib_static")
    assert(r"""
qt_add_library(lib_static STATIC)
target_sources(lib_static PRIVATE
    lib.cpp
)
""" in output)

def test_common_project_types__plugin_shared():
    output = convert("plugin_shared")
    assert(r"""
qt_add_plugin(plugin_shared)
target_sources(plugin_shared PRIVATE
    lib.cpp
)
""" in output)

def test_common_project_types__plugin_static():
    output = convert("plugin_static")
    assert(r"""
qt_add_plugin(plugin_static STATIC)
target_sources(plugin_static PRIVATE
    lib.cpp
)
""" in output)


def test_qml_modules__app_qml_module():
    output = convert("app_qml_module")
    assert(r"""
qt_add_executable(myapp WIN32 MACOSX_BUNDLE)
target_sources(myapp PRIVATE
    donkeyengine.cpp donkeyengine.h
    main.cpp
)
qt_add_qml_module(myapp
    URI DonkeySimulator
    VERSION 1.0
    # qml types are generated by cmake, but not by qmake
    # multiple qml types produce the runtime error
    # "Cannot add multiple registrations for x"
    NO_GENERATE_QMLTYPES
    QML_FILES
        donkey.qml
        waggle_ears.js
    RESOURCES
        bray.ogg
        hoofs.ogg
    NO_RESOURCE_TARGET_PATH
)
""" in output)

def test_qml_modules__lib_qml_module():
    output = convert("lib_qml_module")
    assert(r"""
qt_add_library(lib_qml_module)
target_sources(lib_qml_module PRIVATE
    donkeyengine.cpp donkeyengine.h
)
qt_add_qml_module(lib_qml_module
    URI DonkeySimulator
    VERSION 1.0
    # qml types are generated by cmake, but not by qmake
    # multiple qml types produce the runtime error
    # "Cannot add multiple registrations for x"
    NO_GENERATE_QMLTYPES
    QML_FILES
        donkey.qml
        waggle_ears.js
    RESOURCES
        bray.ogg
        hoofs.ogg
)""" in output)

def test_qml_modules__plugin_qml_module():
    output = convert("plugin_qml_module")
    assert(r"""
qt_add_qml_module(plugin_qml_module
    URI DonkeySimulator
    VERSION 1.0
    # qml types are generated by cmake, but not by qmake
    # multiple qml types produce the runtime error
    # "Cannot add multiple registrations for x"
    NO_GENERATE_QMLTYPES
    QML_FILES
        donkey.qml
        waggle_ears.js
    RESOURCES
        bray.ogg
        hoofs.ogg
    PLUGIN_TARGET plugin_qml_module
)

target_sources(plugin_qml_module PRIVATE
    donkeyengine.cpp donkeyengine.h
)""" in output)


def test_install_commands():
    output = convert("app_install")
    assert(r"""
install(TARGETS app_install
    BUNDLE DESTINATION .
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)""" in output)

    output = convert("lib_install")
    assert(r"""
install(TARGETS lib_install
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)""" in output)


def test_install_targets():
    output = convert("install_targets")
    # note: cmake executes the install commands in order of appearance
    # so the order matters
    assert(r"""
# install_lib
install(TARGETS install_targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# install_c
install_target_files(TARGET "install_targets: c"
    DESTINATION /dst
    SOURCES
    /src/c1.txt
    /src/c2.txt
)

# install_a
# depends on: install_c
install_target_files(TARGET "install_targets: a"
    DESTINATION /dst
    SOURCES
    /src/a
)

# install_b
# depends on: install_a
install_target_files(TARGET "install_targets: b"
    DESTINATION /dst
    SOURCES
    /src/b/
)

# install_distinfo
# depends on: install_lib install_a install_b install_c
install_target_command(TARGET "install_targets: distinfo"
    COMMAND
    sip-distinfo
    --inventory /dst/inventory.txt
    --project-root /src
)
""" in output)


def test_deploy_commands():
    output = convert("app", min_qt_version="6.2")
    assert(r"""
# Consider using qt_generate_deploy_app_script() for app deployment if
# the project can use Qt 6.3. In that case rerun qmake2cmake with
# --min-qt-version=6.3.
""" in output)

    output = convert("app", min_qt_version="6.3")
    assert(r"""
qt_generate_deploy_app_script(
    TARGET app
    FILENAME_VARIABLE deploy_script
    NO_UNSUPPORTED_PLATFORM_ERROR
)
install(SCRIPT ${deploy_script})
""" in output)

    output = convert("app_qml_module", min_qt_version="6.2")
    assert(r"""
# Consider using qt_generate_deploy_app_script() for app deployment if
# the project can use Qt 6.3. In that case rerun qmake2cmake with
# --min-qt-version=6.3.
""" in output)

    output = convert("app_qml_module", min_qt_version="6.3")
    assert(r"""
qt_generate_deploy_qml_app_script(
    TARGET myapp
    FILENAME_VARIABLE deploy_script
    NO_UNSUPPORTED_PLATFORM_ERROR
    DEPLOY_USER_QML_MODULES_ON_UNSUPPORTED_PLATFORM
    MACOS_BUNDLE_POST_BUILD
)
install(SCRIPT ${deploy_script})
""" in output)
