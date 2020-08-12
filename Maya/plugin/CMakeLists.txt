#Main CMakeLists.txt file that includes external modules and cmake instructions

#if the current version of CMake is lower than that required it will stop generating the project and report an error
cmake_minimum_required(VERSION 3.6) 
# this is required by osx, might be depricated in the future
set(CMAKE_MACOSX_RPATH 1)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

set(MAYA_VERSION 2015 CACHE STRING "Maya Version") #can be overriden in a terminal by typing: -DMAYA_VERSION = 2016

#System variable that prevents generating ZERO_CHECK project in an IDE along with other user's custom projects
set(CMAKE_SUPPRESS_REGENERATION true)

# System variable that contains a path which will be used for "include()" and "find_package()" commands
set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

#Finds and loads instructions from an external module
find_package(Maya REQUIRED)

#binary output directories that are specified for different types of a compiled product - Runtime 
if (WIN32)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_CURRENT_SOURCE_DIR}/x64/${MAYA_VERSION}x64)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_CURRENT_SOURCE_DIR}/plug-ins/Debug)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL ${CMAKE_CURRENT_SOURCE_DIR}/plug-ins/MinSizeRel)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO ${CMAKE_CURRENT_SOURCE_DIR}/plug-ins/RelWithDebInfo)
else()
	set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/x64/${MAYA_VERSION}x64)
endif()


# this is where all the projects are added that need to be built
# normally everything would be build in a single plugin, but this allows multiple plugins to be built at once
set(MAYA_PROJECT
	SkinCommands
	CACHE STRING "Maya Project")

#Here we add subdirectories to the build
#projects/${MAYA_PRJ} is a relative directory in which the source CMakeLists.txt and code files are located
foreach(MAYA_PRJ ${MAYA_PROJECT})
	add_subdirectory(projects/${MAYA_PRJ}) 
endforeach()

