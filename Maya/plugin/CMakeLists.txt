#Main CMakeLists.txt file that includes external modules and cmake instructions

#if the current version of CMake is lower than that required it will stop generating the project and report an error
cmake_minimum_required(VERSION 3.6) 
# this is required by osx, might be depricated in the future
set(CMAKE_MACOSX_RPATH 1)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

project(skinCommands)

if(POLICY CMP0072)
    # force the application to take new gl functions instead of legacy
    cmake_policy(SET CMP0072 NEW)
endif()

set(CMAKE_SUPPRESS_REGENERATION true)

get_filename_component(PARENT_DIR ${CMAKE_CURRENT_BINARY_DIR} PATH)

set(CMAKE_INSTALL_PREFIX ${PARENT_DIR}/comp/Maya${MAYA_VERSION} )

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/modules)


# find_package(Maya REQUIRED)
add_subdirectory(projects)
