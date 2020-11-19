#Main CMakeLists.txt file that includes external modules and cmake instructions

#if the current version of CMake is lower than that required it will stop generating the project and report an error
cmake_minimum_required(VERSION 3.6) 
# this is required by osx, might be deprecated in the future
set(CMAKE_MACOSX_RPATH 1)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

project(smooth_brush_maya)

# setup third party libs (Eigen)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/externals/include)

if(POLICY CMP0072)
    # force the application to take new gl functions instead of legacy
    cmake_policy(SET CMP0072 NEW)
endif()

set(CMAKE_SUPPRESS_REGENERATION true)

set(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/lib/maya${MAYA_VERSION}" )

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/modules)

#-------------------------------------------------------------------------------
file(GLOB_RECURSE SOURCE_FILES "*.cpp" "*.h" "*.hpp") 

add_definitions( -DTBX_MAYA_ENABLE_USING_NAMESPACE_TBX_MAYA )
add_definitions( -DTBX_MESH_ENABLE_USING_NAMESPACE_TBX_MESH )
add_definitions( -DTBX_ENABLE_USING_NAMESPACE_TBX )

find_package(Maya REQUIRED)
include_directories(${MAYA_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)

link_directories(${MAYA_LIBRARY_DIR})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${MAYA_LIBRARIES})

MAYA_PLUGIN(${PROJECT_NAME})

message ( "sdfsqdsf ${build_type}")
install(TARGETS ${PROJECT_NAME} ${MAYA_TARGET_TYPE} DESTINATION release)

add_definitions(-D_BOOL -DREQUIRE_IOSTREAM -DMAYA_VERSION=${MAYA_VERSION} -Dbuild_type="release")


if (APPLE)
   add_definitions(-DOSMac_ -DMAC_PLUGIN)
endif()
