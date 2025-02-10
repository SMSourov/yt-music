import os
import sys
import shutil

# Paths to required files
REQUIRED_PROGRAMS_FILE = "docs/required_programs.txt"
REQUIRED_VARIABLES_FILE = "docs/required_variables.txt"
EXECUTABLES_FOLDER = "executables"

# Check if the OS is Windows
IS_WINDOWS = sys.platform.startswith("win")

def check_required_programs():
    """Check if all required programs exist in the 'executables' folder or globally."""
    missing_programs = []
    
    if not os.path.exists(REQUIRED_PROGRAMS_FILE):
        print(f"Error: {REQUIRED_PROGRAMS_FILE} not found.")
        return None  # Return None to indicate a critical error

    with open(REQUIRED_PROGRAMS_FILE, "r") as file:
        programs = [line.strip() for line in file.readlines() if line.strip()]
    
    for program in programs:
        program_path = os.path.join(EXECUTABLES_FOLDER, program)

        # Check if the program exists in 'executables' folder OR is available globally
        if not os.path.isfile(program_path) and shutil.which(program) is None:
            missing_programs.append(program)

    return missing_programs

def check_required_variables():
    """Check if all required environment variables point to existing files."""
    missing_variables = []
    
    if not os.path.exists(REQUIRED_VARIABLES_FILE):
        print(f"Error: {REQUIRED_VARIABLES_FILE} not found.")
        return None  # Return None to indicate a critical error

    with open(REQUIRED_VARIABLES_FILE, "r") as file:
        variables = [line.strip() for line in file.readlines() if line.strip()]

    # Get system PATH directories
    path_dirs = os.environ.get("PATH", "").split(";")

    for var in variables:
        var_name = var + ".exe" if IS_WINDOWS else var  # Append .exe for Windows
        
        # Check if the file exists in any directory listed in PATH
        found = any(os.path.isfile(os.path.join(directory, var_name)) for directory in path_dirs)

        if not found:
            missing_variables.append(var)

    return missing_variables

def main():
    """Run all checks and report missing items."""
    missing_programs = check_required_programs()
    missing_variables = check_required_variables()

    if missing_programs is None or missing_variables is None:
        print("Exiting due to missing requirement files.")
        exit(1)

    if missing_programs or missing_variables:
        print("\n=== Missing Requirements ===")

        if missing_programs:
            print("Missing Programs:")
            for program in missing_programs:
                print(f"- {program}")

        if missing_variables:
            print("Missing Environment Variables (files not found in PATH directories):")
            for var in missing_variables:
                print(f"- {var}")

        print("\nPlease install the missing dependencies before running the program.")
        exit(1)
    
    print("All requirements are met.")

if __name__ == "__main__":
    main()
