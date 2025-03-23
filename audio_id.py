import sys
import os
import subprocess

# Global debug flag
DEBUG_MODE = False

def log_debug(message):
    """Prints debug messages only if debug mode is enabled."""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def validate_input():
    """Validate command-line arguments and check if the JSON file exists."""
    global DEBUG_MODE

    if len(sys.argv) < 2:
        print("Error: No JSON file provided.")
        sys.exit(1)

    args = sys.argv[1:]

    # Check if debug mode is enabled
    if "-d" in args:
        DEBUG_MODE = True
        args.remove("-d")  # Remove debug flag from arguments

    json_file = args[0] if args else None

    if not json_file:
        print("Error: No JSON file provided.")
        sys.exit(1)

    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found.")
        sys.exit(1)

    if not json_file.lower().endswith(".json"):
        print(f"Error: File '{json_file}' is not a JSON file.")
        sys.exit(1)

    log_debug(f"Validated input file: {json_file}")
    return json_file

def run_script(script_name, json_file):
    """Execute a Python script with the given JSON file."""
    command = ["python", script_name, json_file]
    if DEBUG_MODE:
        command.append("-d")  # Pass debug flag if enabled

    log_debug(f"Executing: {' '.join(command)}")

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {script_name} failed.")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout.strip())

def main():
    """Main execution flow."""
    json_file = validate_input()

    # Step 1: Process audio codecs and format notes
    run_script("audio_codecs_qualities.py", json_file)

    # Step 2: Select priority codecs and format notes
    run_script("audio_selections.py", json_file)

if __name__ == "__main__":
    main()
