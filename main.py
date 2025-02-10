import subprocess
import sys
import os

# Ensure requirements.py is executed before proceeding
def check_requirements():
    """Run requirements.py and exit if any requirements are missing."""
    result = subprocess.run([sys.executable, "requirements.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(result.stdout)  # Show missing requirements
        sys.exit(1)

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
            debug_mode = args[debug_index + 1]
        except (IndexError, ValueError):
            print("Error: Debug flag (-d or --debug) requires an argument.")
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

if __name__ == "__main__":
    main()
