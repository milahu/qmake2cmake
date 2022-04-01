cmake_minimum_required(VERSION 3.16)
project(subdirs VERSION 1.0 LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

# Set up AUTOMOC and some sensible defaults for runtime execution
# When using Qt 6.3, you can replace the code block below with
# qt_standard_project_setup()
set(CMAKE_AUTOMOC ON)
include(GNUInstallDirs)

find_package(QT NAMES Qt5 Qt6 REQUIRED COMPONENTS Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Gui Network OpenGL)
find_package(Qt${QT_VERSION_MAJOR} OPTIONAL_COMPONENTS Core5Compat)

qt_add_executable(app WIN32 MACOSX_BUNDLE
    main.cpp
)
target_link_libraries(app PRIVATE
    Qt::OpenGL
)

install(TARGETS app
    BUNDLE DESTINATION .
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# Consider using qt_generate_deploy_app_script() for app deployment if
# the project can use Qt 6.3. In that case rerun qmake2cmake with
# --min-qt-version=6.3.

add_subdirectory(lib1)
add_subdirectory(lib2)
add_subdirectory(lib3)
