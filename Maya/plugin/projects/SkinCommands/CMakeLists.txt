#CMakeLists.txt at ~/projects/testCommand folder
	
project(SkinCommands) #project name

file(GLOB SRCS "*.cpp" "*.h" "*.hpp") #get all files at the current folder with defined extensions

include_directories(${MAYA_INCLUDE_DIR}) #define a list of preprocessor include file search directories

link_directories(${MAYA_LIBRARY_DIR}) #specifies a directory where a linker should search for libraries

add_library(${PROJECT_NAME} SHARED ${SRCS}) #Add a dynamic library to the project using the specified source files

target_link_libraries(${PROJECT_NAME} ${MAYA_LIBRARIES}) #specifies list of libraries to use when linking the terget and its dependents

MAYA_PLUGIN(${PROJECT_NAME}) #runs a function with a PROJECT_NAME as an argument
