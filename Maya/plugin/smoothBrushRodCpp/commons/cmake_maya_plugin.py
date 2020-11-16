import os
import traceback
import platform
import time

#import sys
#sys.path.append("../..") # tell python to add top level directories so we can import from here as well.
from .build_tools import *

'''
    Run cmake script is in charge of calling the cmake command for
    every versions of maya. Basically it calls the following  commands:

    # mkdir build/folders
    # path/to/visual/cvars64.bat // if needed
    # cmake -DMAYA_VERSION=2014 (and a lot of other args ...)
    # jom -j8 // compiles the code
    # cmake -DMAYA_VERSION=2015 (and a lot of other args ...)
    # jom -j8 // compiles the code
    # etc.
'''

# -----------------------------------------------------------------------------

def append_define_args(command_list, list_defines):
    list = command_list
    for (symbol_name, value) in list_defines:
        list += ["-D", symbol_name + "=" + value]
    return list
    
# -----------------------------------------------------------------------------

# @return the cmake command corresponding to cmake_args.
def get_cmake_command_list(cmake_args, list_defines):
    list = ["cmake",
            "-D", "CMAKE_BUILD_TYPE=" + cmake_args['build_type'],
            "-D", "MAYA_VERSION=" + cmake_args['maya_version'],
            "-G", cmake_args['generator']
            ,"-D", "CMAKE_BUILD_ARCH_X64=" + str(int(cmake_args['arch_type'] == "x64"))
            ]
    if( cmake_args['vcs_path'] != ""):
    #if False:
        list += [#"-D", "CMAKE_RC_COMPILER=" + cmake_args['vcs_path'],
                 "-D", "CMAKE_C_COMPILER=cl.exe",
                 "-D", "CMAKE_CXX_COMPILER=cl.exe"]

    if False:
        list += ["-D", "CMAKE_RC_COMPILER=C:/Qt/Tools/mingw730_64/bin",
                 "-D", "CMAKE_C_COMPILER=gcc.exe",
                 "-D", "CMAKE_CXX_COMPILER=g++.exe"]

    if( False ):
        list += ["-D", "CMAKE_C_COMPILER:PATH=C:/Program Files/LLVM/bin/clang.exe",
                 "-D", "CMAKE_CXX_COMPILER:PATH=C:/Program Files/LLVM/bin/clang.exe",
                 "-D", "CMAKE_C_COMPILER_ID=Clang",
                 "-D", "CMAKE_CXX_COMPILER_ID=Clang",
                 "-D", "CMAKE_SYSTEM_NAME=Generic"]

    #if( cmake_args['path_iwyu'] != "" ):
    #    list += ["-D", "CMAKE_CXX_INCLUDE_WHAT_YOU_USE=" + cmake_args['path_iwyu'] ]
        
    list = append_define_args(list, list_defines)

    list += [cmake_args['current_dir']]
    return list
    
# -----------------------------------------------------------------------------
    

# raw bash version of the command
# def get_cmake_command(cmake_args):
    # return ("cmake " +
            # "-DCMAKE_BUILD_TYPE=" + cmake_args['build_type'] + " " +
            # "-DMAYA_VERSION=" + cmake_args['maya_version'] + " " +
            # "-G^\"" + cmake_args['generator'] + "^\"" + " " +
            # "-DCMAKE_BUILD_ARCH_X64=" + str(int(cmake_args['arch_type'] == "x64")) + " " +
            # "-DCMAKE_RC_COMPILER=" + cmake_args['vcs_path'] + " "
            # + cmake_args['current_dir'])


# -----------------------------------------------------------------------------

'''
    arch_string : "x86" or "x64"
    maya_version_list : ["All", "2014", "2015", "2016", "2016.5", "2017", "2018"]
    build_type : ["Debug", "Release", "Both"]
    use_separate_folder_build_folder_maya

'''
def launch(list_defines, arch_string, maya_version_list, build_type, use_separate_folder_build_folder_maya):

    start_time = time.time()
    current_dir = os.getcwd()

    #NOTE: I think cmake will choose the correct Qt version according to the
    #generator if present in the Path, you can set several Qt installs in PATH
    # however qmake.exe -v will be the first occurence in your PATH
    #if not call_command(["qmake.exe", "-v"]):
        #print("WARNING: can't seem to find Qt, check it is defined in your PATH")
        # NOTE: with same make you can force the qt install directory with:
        # "-D", "CMAKE_PREFIX_PATH=C:/Qt/5.12.3/msvc2017_64/"

    cmake_args = {}
    cmake_args['build_type']   = "Release"
    cmake_args['maya_version'] = "UNDEF"

    #cmake_args['generator']    = "NMake Makefiles JOM"
    cmake_args['generator']    = "Ninja"
    #cmake_args['generator']    = "MinGW Makefiles"

    cmake_args['arch_type']    = arch_string
    cmake_args['vcs_path']     = ""
    cmake_args['current_dir']  = current_dir
    #cmake_args['path_iwyu']    = path_iwyu


    build_command = ["jom"] # ["ninja", "-j8"] # possible values "ninja", "jom", "make" etc.
    if( cmake_args['generator'] == "Ninja"):
        build_command = ["ninja"]
    elif( cmake_args['generator'] == "NMake Makefiles JOM"):
        build_command = ["jom"]

    #
    # Setup visual studio env var if needed
    #
    vcs_vars_command = ""

    if platform.system() == "Windows" and cmake_args['generator'] != "MinGW Makefiles":
        vcs_path = os.environ.get('VISUAL_STUDIO_PATH', 'None')
        if vcs_path == "None":
            print("ERROR CAN'T FIND PATH TO VISUAL STUDIO")
            print("please define the environment variable:")
            print("VISUAL_STUDIO_PATH=path_to_visual_compiler_binaries")
            print("the path usually looks like:")
            print("C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\bin")
            sys.exit()

        print("Visual Studio Path: ")
        print(vcs_path)

        vcs_vars_command = find_bat_script(cmake_args['arch_type'], vcs_path)
        cmake_args['vcs_path'] = vcs_path.replace('\\', '/')

    post_command = ["call"] + vcs_vars_command + [ "&"] if (len(vcs_vars_command) > 0) else []

    for maya_version in maya_version_list:

        os.chdir(current_dir)
        print("=========================================================================")
        print("Prep for MAYA"+maya_version)
        print("=========================================================================")
        cmake_args['maya_version'] = maya_version

        if use_separate_folder_build_folder_maya:
            #build_dir_debug   = "build/maya"+maya_version+"/build/release_with_deb_info"
            build_dir_debug   = "build/maya"+maya_version+"/debug"
            build_dir_release = "build/maya"+maya_version+"/release"
        else:
            #build_dir_debug   = "build/release_with_deb_info"
            build_dir_debug   = "build/debug"
            build_dir_release = "build/release"

        print("\n\n== CREATE BUILD DIRECTORIES ==")

        make_dir(build_dir_debug)
        make_dir(build_dir_release)

        if build_type == "Release" or build_type == "Both":
            print("\n\n=== LAUNCH CMAKE RELEASE ===\n")

            os.chdir(current_dir)
            os.chdir(build_dir_release)
            cmake_args['build_type'] = "Release"

            cmake_cmd_list = get_cmake_command_list(cmake_args, list_defines)
            commands = post_command + cmake_cmd_list + ["&"] + build_command            
            call_command(commands)

        if build_type == "Debug" or build_type == "Both":
            print("\n\n=== LAUNCH CMAKE DEBUG ===\n")

            os.chdir(current_dir)
            os.chdir(build_dir_debug)
            cmake_args['build_type'] = "Debug" #"RelWithDebInfo" #"Debug"

            cmake_cmd_list = get_cmake_command_list(cmake_args, list_defines)
            commands = post_command + cmake_cmd_list + ["&"] + build_command
            call_command(commands)

    print("Total build time: " +  str(time.time() - start_time) + " sec\n")
    print("\n========== FINISHED ==========\n")




# -----------------------------------------------------------------------------

def main(list_defines=[]):

    #
    # Setup architecture
    #
   
    #archs = ["x86", "x64"]
    #idx = ask_choice("Choose architecture", archs)
    #arch_string = str(archs[idx])

    #
    # Setup Maya versions
    #

    maya_version_list = ["All", "2017", "2018", "2019", "2020", "2021"] 

    idx = ask_choice("Choose Maya version", maya_version_list)

    if idx == 0: # All versions
        maya_version_list = maya_version_list[1:]
    else: # just one
        maya_version_list = [maya_version_list[idx]]

    builds = ["Debug", "Release", "Both"]
    build_type = builds[ask_choice("Build for", builds)]

    launch([("CMAKE_BUILD_ARCH_X64","1" )]+list_defines, "x64", maya_version_list, build_type, True)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print("Exception raised")
        print(err)
        print("Trace: ")
        print(traceback.print_exc())
    finally:
        wait = input("Press ENTER to continue.")
