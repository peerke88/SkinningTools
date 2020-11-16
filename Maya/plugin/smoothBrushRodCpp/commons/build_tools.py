import sys
import subprocess
import os
import re
from pathlib import Path

# -----------------------------------------------------------------------------

## @param cmd : raw string representing a bat or bash command OR
## a list containing the command name first and then arguments
##
## Notice you can call several commands at a time with "&"
## very useful to save the context (every time you call call_command the context is lost otherwise)
## Ex: call_command(["call", path_to_script.bat, "&"] + another_command list + ["&", "make", "-j8"])
def call_command(cmd):
    try:
        ret_code = subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
    except:
        print("Command failed", flush=True)
        return False
    return (ret_code == 0)


# -----------------------------------------------------------------------------

def call_bat_script(file_path):
    call_command(["call", file_path])

# -----------------------------------------------------------------------------

def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


# -----------------------------------------------------------------------------

def make_dir(path_name):
    if not os.path.exists(path_name):
        os.makedirs(path_name)


# -----------------------------------------------------------------------------

## @return true for input 'y' false otherwise
def ask_yes_no(msge):
    while True:
        res = input(msge + " [y/n] : ")
        if (res in ['y', 'n']):
            break
        else:
            print("Please input \'y\' or \'n\'")

    return (res == 'y')


# -----------------------------------------------------------------------------

## @return the index chose by the user in choice_list
## choice_list[user_index]
def ask_choice(msge, choice_list):
    string = ""
    for idx, val in enumerate(choice_list):
        string = string + str(idx + 1) + ") " + str(val) + "\n"

    while True:
        res = int(input(msge + " : \n" + string + ": "))
        if (res > 0 and res <= len(choice_list)):
            break
        else:
            print("\nPlease input a number ranging from [1, " + str(len(choice_list)) + "]")
    res = res - 1
    print("You choose: " + str(choice_list[res]) + "\n")
    return res

    #return path to vcvars(64/32).bat script

# -----------------------------------------------------------------------------

def find_bat_script(arch, vcs_path):

    # If rc.exe can't be found it means the install of of the windows kit
    # is corrupted try to re-install it through MSVC installer

    # Special case for Visual 2015:
    #if re.compile(".*Microsoft Visual Studio 14\.0.*").match(vcs_path):
    #    return ["C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\VC\\vcvarsall.bat", "amd64"]    # , "8.1"


    #TODO for other versions also rely on vcvarsall.bat instead of vcvars64.bat etc.
    if arch == "x64":
        vcs_vars_script = vcs_path+"\\amd64\\vcvars64.bat"
    else:
        vcs_vars_script = vcs_path+"\\vcvars32.bat"

    if(not os.path.exists(vcs_vars_script)):
        print("Can't find: "+vcs_vars_script)
        print("Try to look up other locations:")
        path_to_script = vcs_path
        while Path(path_to_script).stem != "VC" and path_to_script != Path(path_to_script).parent:
            path_to_script = Path(path_to_script).parent
        path_to_script = os.path.join(path_to_script, "Auxiliary\\Build")

        print("Test for: "+path_to_script)
        if arch == "x64":
            vcs_vars_script = path_to_script+"\\vcvars64.bat"
        else:
            vcs_vars_script = path_to_script+"\\vcvars32.bat"

        if( not os.path.exists(vcs_vars_script) ):
            print("Sorry couldn't find "+vcs_vars_script)
        else:
            print("FOUND!")


    return [vcs_vars_script]

