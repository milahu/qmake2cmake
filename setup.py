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

"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="qmake2cmake",  # Required
    version="1.0.0",  # Required
    description="QMake to CMake project file converter",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://wiki.qt.io/qmake2cmake",  # Optional
    author="The Qt Company",  # Optional
    classifiers=[  # Optional
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="qmake, cmake, development",  # Optional
    packages=["."],  # Required
    python_requires=">=3.7, <4",
    install_requires=["pyparsing", "portalocker", "sympy", "packaging"],  # Optional
    extras_require={  # Optional
        "dev": ["mypy", "flake8", "black"],
        "test": ["pytest", "pytest-cov"],
    },
    entry_points={  # Optional
        "console_scripts": [
            "qmake2cmake=pro2cmake:main",
            "run_qmake2cmake=run_pro2cmake:main",
        ],
    },
    project_urls={  # Optional
        "Bug Reports": "https://bugreports.qt.io/",
        "Source": "https://codereview.qt-project.org/admin/repos/qt/qmake2cmake",
    },
)
