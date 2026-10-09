#Main CMakeLists.txt file that includes external modules and cmake instructions

#if the current version of CMake is lower than that required it will stop generating the project and report an error
cmake_minimum_required(VERSION 3.6) 
# this is required by osx, might be depricated in the future
set(CMAKE_MACOSX_RPATH 1)
if(NOT DEFINED MAYA_VERSION)
    message(FATAL_ERROR "Specify -DMAYA_VERSION=<year> for the target SDK/ABI")
endif()
set(_SKINNINGTOOLS_STANDARD 11)
if(MAYA_VERSION GREATER_EQUAL 2022)
    set(_SKINNINGTOOLS_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD ${_SKINNINGTOOLS_STANDARD} CACHE STRING "C++ standard for the selected Maya SDK")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

project(skinCommands)

if(POLICY CMP0072)
    # force the application to take new gl functions instead of legacy
    cmake_policy(SET CMP0072 NEW)
endif()

set(CMAKE_SUPPRESS_REGENERATION true)

get_filename_component(PARENT_DIR ${CMAKE_CURRENT_BINARY_DIR} PATH)

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/comp/Maya${MAYA_VERSION}" CACHE PATH "Native package destination" FORCE)
endif()

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/modules)


# find_package(Maya REQUIRED)
add_subdirectory(projects)
