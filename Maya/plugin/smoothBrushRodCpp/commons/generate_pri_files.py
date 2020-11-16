import os
import sys
import traceback
import platform
from pathlib import Path

#
# Utilities to generate text files of type '*.pri'
# we generate a list of source files of this project in 
# order to open the various projects with QtCreator, 
# 
#


# Recognized source file extension:
extensions = [".txt", ".TXT", ".cpp", ".c", ".cc", ".cu", ".hpp", ".hh",
              ".inl", ".dox", ".h", ".sh", ".bat", ".py", ".mel", ".cmd",
              ".cmake", ".in", ".frag", ".vert", ".glsl", ".gs", ".vs", 
              ".ui", ".php", ".pro", ".pri", ".htm", ".css"]


# Exclude those folders
folder_exclude_list = [".git",  # excludes any occurence of ".git"
                       "build",  
                       "lib", 
                       "output", 
                       "libraries_third_party/include", # Only exclude this particular folder (starting from root of this script)
                       "libraries_third_party/bin",                       
                       "projects_test",
                       "code_analysis",
                       "__pycache__"]
                       
add_to_include_path = ["src", "include"]

# -----------------------------------------------------------------------------

def exception_summary(err, file_path):
    print("\n------------------------------------------")
    print("CANT READ FILE Exception raised")
    print(err)
    print("Trace: ")
    traceback.print_exc()
    print("file: "+file_path)
    print("------------------------------------------\n")
    sys.stdout.flush()
    
# -----------------------------------------------------------------------------

def write_lines(output_name, lines, option='w+'):
    try:
        with open(output_name, option, encoding="utf-8") as f:
            # go to start of file
            f.seek(0)
            # actually write the lines
            f.writelines(lines)
        return True
    except Exception as err:
        exception_summary(err, output_name)
        return False
    return my_lines
    
# -----------------------------------------------------------------------------

def to_path(a_path):
    return str(Path(a_path))

# -----------------------------------------------------------------------------
    
# The first strips off any trailing slashes, 
# the second gives you the last part of the path.
def get_base_name(a_path):
    return os.path.basename(os.path.normpath(a_path))
    
# -----------------------------------------------------------------------------

# @return 'true' if a folder in 'path' is in the list 'exclude_list'
def is_sub_path(path, start_path, exclude_list):    
    #No more parent folder stop recursion here
    if Path(path).parent == Path(path):
        #print( "end rec")
        return False        

    # quick check if head folder of path matches one of the element of the exclude_list
    # (will only match folder singletons)
    if (str(os.path.basename(path)) in exclude_list):
        return True

    #for excluded in exclude_list:
    #    if Path(path) == Path(excluded)
    #        return True
    #    if Path(os.path.abspath(path)) == Path(os.path.abspath(os.path.join(start_path, excluded))):
    #        return  True

    # The following should actually cover all cases
    # More advanced matching: checks the head of path (any number of folders starting from the head)
    # matches a list of folder from the exclude list
    for excluded in exclude_list:
        if Path(path).match( excluded ):
            return True
        
    return is_sub_path(Path(path).parent, start_path, exclude_list)

# -----------------------------------------------------------------------------

def init(file_list_name, include_path_list_name):
    new_lines = []
    new_lines +=  ["#Define the list of files in this project\n"]
    new_lines +=  [file_list_name+" = \n"]
    new_lines +=  ["#Define the list of folders to be added in the include paths\n"]
    new_lines +=  [include_path_list_name+" = \n"]
    new_lines +=  ["\n"]
    new_lines +=  ["\n"]
    return new_lines

# -----------------------------------------------------------------------------
    
def list_files(walk_from, start_path, file_list_name, folder_exclude_list):    
    global extensions        
    new_lines = []
        
    new_lines +=  [file_list_name+" += \\\n"]

    for root, directories, filenames in os.walk(walk_from, topdown=True):        
        directories[:] = [d for d in directories if not is_sub_path(os.path.join(root, d), walk_from, folder_exclude_list)]
        root = to_path(root)
        #print( root )            
        #if not is_sub_path(root, walk_from, folder_exclude_list):
        for filename in filenames:
            #filename = to_path(filename)
            file     = os.path.join(root, filename)
            #dir      = os.path.dirname(file)
            #top_dir  = os.path.basename( dir )
            is_file  = os.path.isfile(file)
            file_ext = Path(filename).suffix                        
            if is_file and (file_ext in extensions):
                new_lines += [os.path.relpath(file, start_path) + " \\\n"]

    new_lines += new_lines.pop()[:-3]
    return new_lines+["\n\n"]

# -----------------------------------------------------------------------------

def list_include_paths(walk_from, start_path, include_path_list_name, add_to_include_path, folder_exclude_list):    
    global extensions        
    new_lines = []
        
    new_lines +=  [include_path_list_name+" += \\\n"]    
    for root, directories, filenames in os.walk(walk_from):
        directories[:] = [d for d in directories if not is_sub_path(os.path.join(root, d), walk_from, folder_exclude_list)]
        root = to_path(root)
        if Path(root).stem in add_to_include_path:
            #if not is_sub_path(root, walk_from, folder_exclude_list):
            new_lines += [os.path.relpath(root, start_path) + " \\\n"]

    new_lines += new_lines.pop()[:-3]    
    return new_lines+["\n\n"]

# -----------------------------------------------------------------------------

def run():
    global folder_exclude_list    
    global output_file    
    
    # this script's current directory:
    base_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(base_path)
    # path where we generate 'output_file':
    project_path = base_path
    print("Scanning files...\n")    
    new_lines = init(file_list_name, include_path_list_name)
    new_lines += list_files(project_path, base_path, file_list_name, folder_exclude_list)
    new_lines += list_include_paths(project_path, base_path, include_path_list_name, add_to_include_path, folder_exclude_list)
    
    temp_exclude_list.remove("libraries_third_party/include")
    temp_exclude_list = folder_exclude_list+["projects"]
    root = os.path.abspath(Path(project_path).parent.parent)
    new_lines += list_files(root, base_path, file_list_name, temp_exclude_list)
    new_lines += list_include_paths(root, base_path, include_path_list_name, add_to_include_path, temp_exclude_list)
    write_lines(output_file, new_lines)  

# -----------------------------------------------------------------------------
