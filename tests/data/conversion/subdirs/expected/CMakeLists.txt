cmake_minimum_required(VERSION 3.16)
project(subdirs VERSION 1.0 LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

# Set up AUTOMOC and some sensible defaults for runtime execution
# When using Qt 6.3, you can replace the code block below with
# qt_standard_project_setup()
set(CMAKE_AUTOMOC ON)
include(GNUInstallDirs)


# helper functions

function(get_name_of_path path result)
    # get basename of filepath or dirname of dirpath
    cmake_path(SET path NORMALIZE "${path}")
    string(REGEX REPLACE "(.)/$" "\\1" path "${path}")
    cmake_path(GET path FILENAME name)
    set(${result} "${name}" PARENT_SCOPE)
endfunction()

function(get_dst_of_src src dstdir result)
    get_name_of_path("${src}" name)
    cmake_path(APPEND dst "${dstdir}" "${name}")
    set(${result} "${dst}" PARENT_SCOPE)
endfunction()

macro(install_target_files)
    cmake_parse_arguments("ARG" "" "TARGET;DESTINATION" "SOURCES" ${ARGN})
    if(NOT ARG_TARGET)
        message(FATAL_ERROR "install_target_files: missing argument: TARGET")
    endif()
    if(NOT ARG_DESTINATION)
        message(FATAL_ERROR "install_target_files: missing argument: DESTINATION")
    endif()
    if(NOT ARG_SOURCES)
        message(FATAL_ERROR "install_target_files: missing argument: SOURCES")
    endif()
    foreach(src ${ARG_SOURCES})
        get_dst_of_src("${src}" "${ARG_DESTINATION}" dst)
        install(CODE "message(STATUS \"Installing: ${ARG_TARGET}: ${dst}\")")
        #install(CODE "message([[file(COPY \"${src}\" DESTINATION \"${ARG_DESTINATION}/\")]])")
        install(CODE "file(COPY \"${src}\" DESTINATION \"${ARG_DESTINATION}/\")")
    endforeach()
endmacro()

macro(install_target_command)
    cmake_parse_arguments("ARG" "" "TARGET;WORKING_DIRECTORY" "COMMAND" ${ARGN})
    if(NOT ARG_TARGET)
        message(FATAL_ERROR "install_target_files: missing argument: TARGET")
    endif()
    # ARG_DESTINATION is not used by qmake
    # TODO ARG_WORKING_DIRECTORY? pass WORKING_DIRECTORY to execute_process?
    if(NOT ARG_COMMAND)
        message(FATAL_ERROR "install_target_files: missing argument: COMMAND")
    endif()
    # escape hell ...
    set(args ${ARG_COMMAND})
    list(TRANSFORM args REPLACE [["]] [[\\"]])
    list(TRANSFORM args REPLACE "\n" "\\\\n")
    list(TRANSFORM args REPLACE "\r" "\\\\r")
    list(TRANSFORM args REPLACE "\t" "\\\\t")
    set(escargs) # empty list
    foreach(arg ${args})
        if(arg MATCHES "[ \\]")
            list(APPEND escargs "\"${arg}\"") # wrap in quotes
        else()
            list(APPEND escargs "${arg}")
        endif()
    endforeach()
    list(JOIN escargs " " arg_str)
    set(arg_str_esc "${arg_str}")
    string(REGEX REPLACE [[\\]] [[\\\\]] arg_str_esc "${arg_str_esc}")
    string(REGEX REPLACE [["]] [[\\"]] arg_str_esc "${arg_str_esc}")
    install(CODE "message(STATUS \"Running: ${ARG_TARGET}: ${arg_str_esc}\")")
    install(CODE "execute_process(COMMAND ${arg_str} COMMAND_ERROR_IS_FATAL ANY)")
endmacro()

# declare dependencies between subdirectories
# https://gitlab.kitware.com/cmake/cmake/-/issues/23626
function(add_subdirectory_ordered)
    # build subdirectories in order
    # note: this can break in edge-cases
    # https://gitlab.kitware.com/cmake/cmake/-/issues/22157
    list(JOIN ARGV " " argv_str) # TODO quote args
    message(VERBOSE "add_subdirectory_ordered: add_subdirectory(${argv_str})")
    # https://cmake.org/cmake/help/latest/command/add_subdirectory.html
    # add_subdirectory(source_dir [binary_dir] [EXCLUDE_FROM_ALL])
    add_subdirectory(${ARGV})
    list(GET ARGV 0 source_dir)
    get_property(last_subdir_all_targets DIRECTORY "${source_dir}" PROPERTY BUILDSYSTEM_TARGETS)
    set(last_subdir_main_targets)
    foreach(subdir_target ${last_subdir_all_targets})
        get_property(type TARGET ${subdir_target} PROPERTY TYPE)
        if(type STREQUAL "EXECUTABLE" OR type MATCHES "LIBRARY$")
            message(VERBOSE "add_subdirectory_ordered: target ${subdir_target} has type ${type} -> is a main target")
            list(APPEND last_subdir_main_targets ${subdir_target})
        else()
            message(VERBOSE "add_subdirectory_ordered: target ${subdir_target} has type ${type} -> is not a main target")
        endif()
    endforeach()
    if(all_previous_targets)
        foreach(subdir_target ${last_subdir_main_targets})
            list(JOIN all_previous_targets " " all_previous_targets_str)
            message(STATUS "add_subdirectory_ordered: build order: ${all_previous_targets_str} ${subdir_target}")
            add_dependencies(${subdir_target} ${all_previous_targets})
        endforeach()
    endif()
    set(all_previous_targets_local ${all_previous_targets})
    list(APPEND all_previous_targets_local ${last_subdir_main_targets})
    set(all_previous_targets ${all_previous_targets_local} PARENT_SCOPE)
endfunction()


find_package(QT NAMES Qt5 Qt6 REQUIRED)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Gui Network OpenGL)
find_package(Qt${QT_VERSION_MAJOR} OPTIONAL_COMPONENTS Core5Compat)

qt_add_executable(app WIN32 MACOSX_BUNDLE)
target_sources(app PRIVATE
    main.cpp
)
target_link_libraries(app PRIVATE
    Qt::OpenGL
)

# install_app
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
