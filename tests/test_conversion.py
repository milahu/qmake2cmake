#!/usr/bin/env python3
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from qmake2cmake.pro2cmake import Scope, SetOperation, merge_scopes, recursive_evaluate_scope
from qmake2cmake.pro2cmake import main as convert_qmake_to_cmake
from tempfile import TemporaryDirectory

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
default_min_qt_version = "6.2.0"

def compare_expected_output_directories(actual: str, expected: str):
    dc = filecmp.dircmp(actual, expected)
    assert(dc.diff_files == [])


def convert(base_name: str,
            *,
            min_qt_version: str = default_min_qt_version,
            after_conversion_hook: Optional[Callable[[str], None]] = None):
    '''Converts {base_name}.pro to CMake in a temporary directory.

    The optional after_conversion_hook is a function that takes the temporary directory as
    parameter.  It is called after the conversion took place.
    '''
    pro_file_name = str(base_name) + ".pro"
    pro_file_path = test_data_dir.joinpath(pro_file_name)
    assert(pro_file_path.exists())
    with TemporaryDirectory(prefix="testqmake2cmake") as tmp_dir_str:
        tmp_dir = pathlib.Path(tmp_dir_str)
        output_file_path = tmp_dir.joinpath("CMakeLists.txt")
        convert_qmake_to_cmake(["-o", str(output_file_path), str(pro_file_path),
                                "--min-qt-version", min_qt_version])
        if debug_mode:
            output_dir = tempfile.gettempdir() + "/qmake2cmake/" + base_name
            if min_qt_version != default_min_qt_version:
                output_dir += "-"
                output_dir += min_qt_version
            if not os.path.isdir(output_dir):
                os.mkdir(output_dir)
            shutil.copyfile(output_file_path, output_dir + "/CMakeLists.txt")
        with open(output_file_path, "r") as f:
            assert(f)
            content = f.read()
        assert(content)
        if after_conversion_hook is not None:
            after_conversion_hook(tmp_dir)
        return content


def convert_and_compare_expected_output(pro_base_name: str, rel_expected_output_dir: str):
    abs_expected_output_dir = test_data_dir.joinpath(rel_expected_output_dir)
    convert(pro_base_name,
            after_conversion_hook=functools.partial(compare_expected_output_directories,
                                                    expected=abs_expected_output_dir))


def test_qt_modules():
    '''Test the conversion of QT assignments to find_package calls.'''
    output = convert("required_qt_modules")
    find_package_lines = []
    for line in output.split("\n"):
        if "find_package(" in line:
            find_package_lines.append(line.strip())
    assert(["find_package(QT NAMES Qt5 Qt6 REQUIRED COMPONENTS Core)",
            "find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Network Widgets)"] == find_package_lines)

    output = convert("optional_qt_modules")
    find_package_lines = []
    for line in output.split("\n"):
        if "find_package(" in line:
            find_package_lines.append(line.strip())
    assert(["find_package(QT NAMES Qt5 Qt6 REQUIRED COMPONENTS Core)",
            "find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Network Widgets)",
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
    convert_and_compare_expected_output("subdirs/subdirs", "subdirs/expected")


def test_common_project_types():
    output = convert("app")
    assert(r"""
qt_add_executable(app WIN32 MACOSX_BUNDLE
    main.cpp
)""" in output)

    output = convert("app_cmdline")
    assert(r"""
qt_add_executable(myapp
    main.cpp
)""" in output)

    output = convert("app_console")
    assert(r"""
qt_add_executable(myapp MACOSX_BUNDLE
    main.cpp
)""" in output)

    output = convert("app_nonbundle")
    assert(r"""
qt_add_executable(myapp WIN32
    main.cpp
)""" in output)

    output = convert("lib_shared")
    assert(r"""
qt_add_library(lib_shared
    lib.cpp
)""" in output)

    output = convert("lib_static")
    assert(r"""
qt_add_library(lib_static STATIC
    lib.cpp
)""" in output)

    output = convert("plugin_shared")
    assert(r"""
qt_add_plugin(plugin_shared)
target_sources(plugin_shared PRIVATE
    lib.cpp
)""" in output)

    output = convert("plugin_static")
    assert(r"""
qt_add_plugin(plugin_static STATIC)
target_sources(plugin_static PRIVATE
    lib.cpp
)""" in output)

    output = convert("plugin_shared", min_qt_version = "6.5.0")
    assert(r"""
qt_add_plugin(plugin_shared
    lib.cpp
)""" in output)

    output = convert("plugin_static", min_qt_version = "6.5.0")
    assert(r"""
qt_add_plugin(plugin_static STATIC
    lib.cpp
)""" in output)


def test_qml_modules():
    output = convert("app_qml_module")
    assert(r"""
qt_add_executable(myapp WIN32 MACOSX_BUNDLE
    donkeyengine.cpp donkeyengine.h
    main.cpp
)
qt_add_qml_module(myapp
    URI DonkeySimulator
    VERSION 1.0
    QML_FILES
        donkey.qml
        waggle_ears.js
    RESOURCES
        bray.ogg
        hoofs.ogg
    NO_RESOURCE_TARGET_PATH
)
""" in output)

    output = convert("lib_qml_module")
    assert(r"""
qt_add_library(lib_qml_module
    donkeyengine.cpp donkeyengine.h
)
qt_add_qml_module(lib_qml_module
    URI DonkeySimulator
    VERSION 1.0
    QML_FILES
        donkey.qml
        waggle_ears.js
    RESOURCES
        bray.ogg
        hoofs.ogg
)""" in output)

    output = convert("plugin_qml_module")
    assert(r"""
qt_add_qml_module(plugin_qml_module
    URI DonkeySimulator
    VERSION 1.0
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
