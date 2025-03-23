import sys
import subprocess

# Global debug flag
DEBUG_MODE = "-d" in sys.argv

def validate_input():
    """Validate that a JSON file is provided."""
    args = [arg for arg in sys.argv[1:] if arg != "-d"]

    if not args:
        print("Error: No JSON file provided.")
        sys.exit(1)

    return args[0]  # Return the JSON filename

def run_script(script_name, json_file):
    """Execute a Python script with the JSON file."""
    command = ["python", script_name, json_file]
    if DEBUG_MODE:
        command.append("-d")  # Pass debug flag if enabled

    subprocess.run(command, check=True)

def main():
    """Launch audio selection scripts with JSON file."""
    json_file = validate_input()

    run_script("audio_selections_format_notes.py", json_file)
    run_script("audio_selections_codecs.py", json_file)

if __name__ == "__main__":
    main()
