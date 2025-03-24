import sys
import os
import json

# File paths
AUDIO_CODEC_FILE = "docs/audio_codecs.txt"
AUDIO_FORMAT_NOTES_FILE = "docs/audio_format_notes.txt"

# Global debug flag
DEBUG_MODE = False

def log_debug(message):
    """Prints debug messages only if debug mode is enabled."""
    if DEBUG_MODE:
        try:
            print(f"[DEBUG] {message}")
        except UnicodeEncodeError:
            print(f"[DEBUG] {message}".encode("ascii", "ignore").decode("ascii"))

def validate_input():
    """Validate command-line arguments and check if debug mode is enabled."""
    global DEBUG_MODE
    
    if "-d" in sys.argv:
        DEBUG_MODE = True
        sys.argv.remove("-d")
    
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

def load_prioritized_data(file_path):
    """Load codecs or format notes, preserving priority markers (@, #)."""
    primary, secondary = None, None
    
    if not os.path.exists(file_path):
        log_debug(f"File '{file_path}' does not exist. Skipping.")
        return primary, secondary
    
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("@"): 
                primary = line[1:]
            elif line.startswith("#") and secondary is None:
                secondary = line[1:]
    
    log_debug(f"Loaded priority data from {file_path}: Primary: {primary}, Secondary: {secondary}")
    return primary, secondary

def find_matching_format_id(json_data, primary_codec, secondary_codec, primary_note, secondary_note):
    """Find format_id based on codec and format note priority."""
    format_id_candidates = []
    selected_format_id = None

    log_debug(f"Searching for format IDs with primary_codec={primary_codec}, secondary_codec={secondary_codec}, primary_note={primary_note}, secondary_note={secondary_note}")

    for fmt in json_data.get("formats", []):
        if fmt.get("acodec") == "none":
            continue  # Skip non-audio formats

        fmt_codec = fmt.get("acodec")
        fmt_note = fmt.get("format_note")
        fmt_id = fmt.get("format_id")

        log_debug(f"Checking format: ID={fmt_id}, Codec={fmt_codec}, Note={fmt_note}")

        # Priority 1: Highest codec + highest format note
        if fmt_codec == primary_codec and fmt_note == primary_note:
            log_debug(f"✅ Found exact match: {fmt_id} (Primary Codec + Primary Note)")
            print(fmt_id)
            return

        # Priority 2: Highest codec + secondary format note
        if fmt_codec == primary_codec and fmt_note == secondary_note:
            log_debug(f"⚠️ Found match: {fmt_id} (Primary Codec + Secondary Note)")
            selected_format_id = fmt_id

        # Priority 3: Highest codec, ignore format note
        if fmt_codec == primary_codec and not selected_format_id:
            log_debug(f"⚠️ Found match: {fmt_id} (Primary Codec, ignoring Note)")
            selected_format_id = fmt_id

        # Priority 4: Secondary codec + highest format note
        if fmt_codec == secondary_codec and fmt_note == primary_note and not selected_format_id:
            log_debug(f"⚠️ Found match: {fmt_id} (Secondary Codec + Primary Note)")
            selected_format_id = fmt_id

        # Priority 5: Secondary codec + secondary format note
        if fmt_codec == secondary_codec and fmt_note == secondary_note and not selected_format_id:
            log_debug(f"⚠️ Found match: {fmt_id} (Secondary Codec + Secondary Note)")
            selected_format_id = fmt_id

        # Priority 6: Secondary codec, ignore format note
        if fmt_codec == secondary_codec and not selected_format_id:
            log_debug(f"⚠️ Found match: {fmt_id} (Secondary Codec, ignoring Note)")
            selected_format_id = fmt_id

    if selected_format_id:
        log_debug(f"✅ Using best available match: {selected_format_id}")
        print(selected_format_id)
    else:
        log_debug("⚠️ No suitable match found. Using 'av'.")
        print("av")

def process_audio_format_ids(json_file):
    """Main process to find audio format IDs."""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            metadata = json.load(file)
    except Exception as e:
        print(f"Error: Failed to read JSON file. {e}")
        sys.exit(1)

    if "formats" not in metadata:
        print("Error: 'formats' data missing in JSON file.")
        sys.exit(1)

    primary_codec, secondary_codec = load_prioritized_data(AUDIO_CODEC_FILE)
    primary_note, secondary_note = load_prioritized_data(AUDIO_FORMAT_NOTES_FILE)

    if not primary_codec:
        print("Error: No priority codec found.")
        sys.exit(1)

    find_matching_format_id(metadata, primary_codec, secondary_codec, primary_note, secondary_note)

def main():
    """Main execution."""
    json_file = validate_input()
    process_audio_format_ids(json_file)

if __name__ == "__main__":
    main()
