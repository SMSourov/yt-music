import subprocess
import sys
import os

# Import the generate_unique_filename function
from generate_temp_filename import generate_unique_filename

# Ensure requirements.py is executed before proceeding
def check_requirements():
    """Run requirements.py and exit if any requirements are missing."""
    result = subprocess.run([sys.executable, "requirements.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(result.stdout)  # Show missing requirements
        sys.exit(1)

def is_json_file(filename):
    """Check if the given filename is a JSON file."""
    return filename.lower().endswith(".json")

def main():
    """Main program execution."""
    # Run requirements check first
    check_requirements()

    # Check for arguments
    if len(sys.argv) < 2:
        print("Error: No link provided. Usage: main.py <link> [-d debug_mode]")
        sys.exit(1)

    # Handle arguments
    link = None
    debug_mode = None

    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        # Display help file
        help_file = "docs/help.txt"
        if os.path.exists(help_file):
            with open(help_file, "r") as file:
                print(file.read())
        else:
            print("Error: Help file not found.")
        sys.exit(0)

    if "-d" in args or "--debug" in args:
        try:
            debug_index = args.index("-d") if "-d" in args else args.index("--debug")
            debug_file = args[debug_index + 1]

            # Check if the file exists and is a JSON file
            if not os.path.exists(debug_file):
                print(f"Error: Debug file '{debug_file}' does not exist.")
                sys.exit(1)

            if not is_json_file(debug_file):
                print(f"Error: Debug file '{debug_file}' is not a JSON file.")
                sys.exit(1)

            print(f"Debug Mode: Using JSON file '{debug_file}'")
            sys.exit(0)  # Exit after validation
        except (IndexError, ValueError):
            print("Error: Debug flag (-d or --debug) requires a file argument.")
            sys.exit(1)

    # Extract the link
    for arg in args:
        if arg.startswith("http"):
            link = arg
            break

    if not link:
        print("Error: No valid link provided.")
        sys.exit(1)

    # Display the given input
    print(f"Input Link: {link}")
    if debug_mode:
        print(f"Debug Mode: {debug_mode}")
        sys.exit(0)  # Skip processing if debug mode is enabled

    # Generate a unique filename
    temp_filename = generate_unique_filename()

    # Execute yt-dlp command
    command = ["py", "./executables/yt-dlp", "-j", link]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        # Save JSON output to the generated filename
        with open(temp_filename, "w", encoding="utf-8") as file:
            file.write(result.stdout)
        print(f"Metadata saved as: {temp_filename}")
    else:
        print("Error: Failed to retrieve metadata.")
        print(result.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
