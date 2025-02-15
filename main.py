import subprocess
import sys
import os
import json

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

def read_metadata_file(filename):
    """Read and return the contents of a JSON metadata file."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            metadata = json.load(file)
            return metadata
    except Exception as e:
        print(f"Error: Failed to read JSON file '{filename}'. Reason: {e}")
        sys.exit(1)

def fetch_metadata(link):
    """Fetch metadata using yt-dlp and save it as a JSON file."""
    temp_filename = generate_unique_filename()
    command = ["py", "./executables/yt-dlp", "-j", link]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        with open(temp_filename, "w", encoding="utf-8") as file:
            file.write(result.stdout)
        print(f"Metadata saved as: {temp_filename}")
        return temp_filename
    else:
        print("Error: Failed to retrieve metadata.")
        print(result.stderr)
        sys.exit(1)

def main():
    """Main program execution."""
    # Run requirements check first
    check_requirements()

    # Check for arguments
    if len(sys.argv) < 2:
        print("Error: No input provided. Usage: main.py <link> OR main.py -d <filename>")
        sys.exit(1)

    args = sys.argv[1:]
    metadata_file = None

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
            metadata_file = args[debug_index + 1]

            # Check if the file exists and is a JSON file
            if not os.path.exists(metadata_file):
                print(f"Error: Debug file '{metadata_file}' does not exist.")
                sys.exit(1)

            if not is_json_file(metadata_file):
                print(f"Error: Debug file '{metadata_file}' is not a JSON file.")
                sys.exit(1)

        except (IndexError, ValueError):
            print("Error: Debug flag (-d or --debug) requires a file argument.")
            sys.exit(1)

    else:
        # Extract the link
        link = None
        for arg in args:
            if arg.startswith("http"):
                link = arg
                break

        if not link:
            print("Error: No valid link provided.")
            sys.exit(1)

        print(f"Input Link: {link}")
        metadata_file = fetch_metadata(link)  # Get metadata and save it

    # Read the metadata file
    metadata = read_metadata_file(metadata_file)

    # Continue with other tasks using the metadata...
    print("Metadata successfully loaded. Proceeding with other tasks...")

if __name__ == "__main__":
    main()
