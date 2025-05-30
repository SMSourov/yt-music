import sys
import os
import json

# File paths
AUDIO_CODEC_FILE = "docs/audio_codecs.txt"
AUDIO_FORMAT_NOTE_FILE = "docs/audio_format_notes.txt"

# Global debug flag
DEBUG_MODE = False

def log_debug(message):
    """Prints debug messages only if debug mode is enabled."""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def validate_input():
    """Validate command-line arguments and check if debug mode is enabled."""
    global DEBUG_MODE

    if "-d" in sys.argv:
        DEBUG_MODE = True
        sys.argv.remove("-d")  # Remove debug flag from arguments

    if len(sys.argv) < 2:
        print("Error: No JSON file provided.")
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found.")
        sys.exit(1)

    if not json_file.lower().endswith(".json"):
        print(f"Error: File '{json_file}' is not a JSON file.")
        sys.exit(1)

    log_debug(f"Validated input file: {json_file}")
    return json_file

def load_json(json_file):
    """Load JSON data from the provided file."""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            log_debug("Successfully loaded JSON data.")
            return data
    except Exception as e:
        print(f"Error: Failed to read JSON file '{json_file}'. Reason: {e}")
        sys.exit(1)

def normalize_audio_codec(acodec):
    """Normalize audio codec names for consistency."""
    acodec = acodec.strip().lower()
    if acodec.startswith("mp4a"):
        return "mp4a"
    return acodec

def load_existing_priorities(filepath):
    """Load existing priority markers (`@`, `#`) from a file."""
    priorities = {}  # Dictionary to store codec -> marker mapping

    if not os.path.exists(filepath):
        return priorities  # Return empty if file does not exist

    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            marker = ""
            if line.startswith("@") or line.startswith("#"):
                marker, codec = line[0], line[1:].strip()
            else:
                codec = line.strip()

            priorities[codec] = marker  # Store marker for each codec

    return priorities

def save_sorted_data(filepath, data, existing_priorities):
    """Save sorted data to a file while preserving priority markers."""
    sorted_codecs = sorted(set(data))  # Sort without markers

    with open(filepath, "w", encoding="utf-8") as file:
        for codec in sorted_codecs:
            marker = existing_priorities.get(codec, "")  # Get existing marker
            file.write(f"{marker}{codec}\n")

def process_audio_data(json_file):
    """Extract and update audio codec and format note files."""
    metadata = load_json(json_file)

    if "formats" not in metadata:
        print("Error: 'formats' data missing in JSON file.")
        sys.exit(1)

    audio_codecs = set()
    format_notes = set()

    for fmt in metadata["formats"]:
        acodec = normalize_audio_codec(fmt.get("acodec", "none"))
        format_note = fmt.get("format_note", "").strip()

        if acodec == "none":
            continue  # Ignore non-audio formats

        if acodec:
            audio_codecs.add(acodec)
        if format_note:
            format_notes.add(format_note)

    log_debug(f"Extracted {len(audio_codecs)} unique audio codecs.")
    log_debug(f"Extracted {len(format_notes)} unique format notes.")

    # Load existing priority markers before saving
    existing_codec_priorities = load_existing_priorities(AUDIO_CODEC_FILE)
    existing_format_priorities = load_existing_priorities(AUDIO_FORMAT_NOTE_FILE)

    save_sorted_data(AUDIO_CODEC_FILE, audio_codecs, existing_codec_priorities)
    save_sorted_data(AUDIO_FORMAT_NOTE_FILE, format_notes, existing_format_priorities)

    # print(f"Updated {AUDIO_CODEC_FILE} and {AUDIO_FORMAT_NOTE_FILE}")

def main():
    """Main execution."""
    json_file = validate_input()
    process_audio_data(json_file)

if __name__ == "__main__":
    main()
