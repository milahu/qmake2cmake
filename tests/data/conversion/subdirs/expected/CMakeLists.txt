# Generated from subdirs.pro.

cmake_minimum_required(VERSION 3.16)
project(subdirs VERSION 1.0 LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_AUTOMOC ON)

find_package(QT NAMES Qt5 Qt6 REQUIRED COMPONENTS Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS OpenGL)

qt_add_executable(app WIN32 MACOSX_BUNDLE
    main.cpp
)
target_link_libraries(app PUBLIC
    Qt::OpenGL
)
add_subdirectory(lib1)
add_subdirectory(lib2)
add_subdirectory(lib3)
