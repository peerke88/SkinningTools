import sys
import commons.cmake_maya_plugin as run_cmake

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_cmake.main()
    except Exception as err:
        print("Exception raised")
        print(err)
        print("Trace: ")
        print(traceback.print_exc())
    finally:
        wait = input("Press ENTER to continue.")
