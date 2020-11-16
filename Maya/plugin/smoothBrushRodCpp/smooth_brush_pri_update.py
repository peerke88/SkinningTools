import sys
import commons.generate_pri_files as gen_pri

from pathlib import Path
import os

# Generate the file 'output_file'
# With the list of all the source files in this project stored in the variable
# 'file_list_name'
# (useful for loading the project into Qt creator)
#

output_file = "smooth_brush.pri"

# variable name where we store the list of files
file_list_name = "SMOOTH_BRUSH_FILES"

include_path_list_name = "SMOOTH_BRUSH_INCLUDEPATH"

# -----------------------------------------------------------------------------

def run():    
    global output_file    
    exclude_list = gen_pri.folder_exclude_list    
    
    # this script's current directory:
    base_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(base_path)
    # path where we generate 'output_file':
    project_path = base_path
    print("Scanning files...\n")    
    new_lines  = gen_pri.init(file_list_name, include_path_list_name)
    new_lines += gen_pri.list_files(project_path, base_path, file_list_name, exclude_list)
    new_lines += gen_pri.list_include_paths(project_path, base_path, include_path_list_name, gen_pri.add_to_include_path, exclude_list)    
    
    gen_pri.write_lines(output_file, new_lines)  

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    try:        
        run()        
    except Exception as err:
        print("Exception raised")
        print(err)
        print("Trace: ")
        print(traceback.print_exc())
    finally:
        wait = input("DONE: press ENTER to continue.")
