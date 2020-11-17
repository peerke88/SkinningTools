file(GLOB_RECURSE SOURCE_FILES "*.cpp" "*.h" "*.hpp") 

add_definitions( -DTBX_MAYA_ENABLE_USING_NAMESPACE_TBX_MAYA )
add_definitions( -DTBX_MESH_ENABLE_USING_NAMESPACE_TBX_MESH )
add_definitions( -DTBX_ENABLE_USING_NAMESPACE_TBX )

find_package(Maya REQUIRED)
include_directories(${MAYA_INCLUDE_DIR} ${PARENT_DIR}/src)

link_directories(${MAYA_LIBRARY_DIR})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${MAYA_LIBRARIES})

MAYA_PLUGIN(${PROJECT_NAME})

install(TARGETS ${PROJECT_NAME} ${MAYA_TARGET_TYPE} DESTINATION plug-ins)

add_definitions(-D_BOOL -DREQUIRE_IOSTREAM -DMAYA_VERSION=${MAYA_VERSION})


if (APPLE)
   add_definitions(-DOSMac_ -DMAC_PLUGIN)
endif()
