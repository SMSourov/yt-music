import sys
import os
import json

# File paths
RES_LANDSCAPE_FILE = "docs/video_resolutions_landscape.txt"
RES_PORTRAIT_FILE = "docs/video_resolutions_portrait.txt"
VIDEO_CODEC_FILE = "docs/video_codecs.txt"

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

def load_prioritized_data(file_path):
    """Load resolutions or codecs, preserving priority markers (@, #)."""
    primary, secondary = None, None

    if not os.path.exists(file_path):
        log_debug(f"File '{file_path}' does not exist. Skipping.")
        return primary, secondary

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("@"):
                primary = line[1:]  # Highest priority
            elif line.startswith("#") and secondary is None:
                secondary = line[1:]  # Second priority

    log_debug(f"Loaded priority data from {file_path}: Primary: {primary}, Secondary: {secondary}")
    return primary, secondary

def normalize_codec(codec):
    """Normalize codec names for consistent matching."""
    if codec.startswith("vp09") or codec == "vp9":
        return "vp09"
    elif codec.startswith("avc1"):
        return "avc1"
    elif codec.startswith("av01"):
        return "av01"
    return codec  # Keep as is for unrecognized formats

def determine_orientation(json_data):
    """Determine whether the video is landscape or portrait."""
    max_width, max_height = 0, 0

    for fmt in json_data.get("formats", []):
        width, height = fmt.get("width"), fmt.get("height")
        if width and height and width * height > max_width * max_height:
            max_width, max_height = width, height

    orientation = "Landscape" if max_width >= max_height else "Portrait"
    log_debug(f"Determined Video Orientation: {orientation}")
    return orientation

def find_matching_format_ids(json_data, width, height, primary_codec, secondary_codec):
    """Find `format_id` based on resolution and codec priority."""
    format_id_candidates = []
    selected_format_id = None

    log_debug(f"Searching for format IDs with width={width}, height={height}, primary_codec={primary_codec}, secondary_codec={secondary_codec}")

    for fmt in json_data.get("formats", []):
        if fmt.get("vcodec") == "none":
            continue  # Skip non-video formats

        fmt_width, fmt_height = fmt.get("width"), fmt.get("height")
        fmt_codec = normalize_codec(fmt.get("vcodec"))
        fmt_id = fmt.get("format_id")

        log_debug(f"Checking format: ID={fmt_id}, Width={fmt_width}, Height={fmt_height}, Codec={fmt_codec}")

        # Match resolution (width first, then height)
        if fmt_width == width or fmt_height == height:
            format_id_candidates.append(fmt_id)

            # Match primary codec (`@codec`)
            if fmt_codec == primary_codec:
                log_debug(f"✅ Found exact match: {fmt_id} (Primary Codec)")
                print(fmt_id)  # Print immediately if perfect match
                return

            # Match secondary codec (`#codec`)
            if fmt_codec == secondary_codec and selected_format_id is None:
                log_debug(f"⚠️ Found second priority match: {fmt_id} (Secondary Codec)")
                selected_format_id = fmt_id

    # Print best alternative or fallback
    if selected_format_id:
        log_debug(f"✅ Using secondary codec match: {selected_format_id}")
        print(selected_format_id)
    elif format_id_candidates:
        log_debug(f"✅ Using best available resolution match: {format_id_candidates[0]}")
        print(format_id_candidates[0])  # Print first available resolution match
    else:
        log_debug(f"⚠️ No matching format found. Using 'bv'.")
        print("bv", end="")  # No match found

def process_format_ids(json_file):
    """Main process to find format IDs."""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            metadata = json.load(file)
    except Exception as e:
        print(f"Error: Failed to read JSON file. {e}")
        sys.exit(1)

    if "formats" not in metadata:
        print("Error: 'formats' data missing in JSON file.")
        sys.exit(1)

    # Determine orientation
    orientation = determine_orientation(metadata)

    # Select appropriate resolution file
    res_file = RES_LANDSCAPE_FILE if orientation == "Landscape" else RES_PORTRAIT_FILE
    primary_res, secondary_res = load_prioritized_data(res_file)
    primary_codec, secondary_codec = load_prioritized_data(VIDEO_CODEC_FILE)

    if not primary_res:
        print("Error: No priority resolution found.")
        sys.exit(1)

    width, height = map(int, primary_res.split("x"))
    find_matching_format_ids(metadata, width, height, primary_codec, secondary_codec)

def main():
    """Main execution."""
    json_file = validate_input()
    process_format_ids(json_file)

if __name__ == "__main__":
    main()
