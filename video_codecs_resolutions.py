import sys
import os
import json
import re

# File paths
RES_LANDSCAPE_FILE = "docs/video_resolutions_landscape.txt"
RES_PORTRAIT_FILE = "docs/video_resolutions_portrait.txt"
VIDEO_CODEC_FILE = "docs/video_codecs.txt"

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

def determine_orientation(width, height):
    """Determine whether the video is landscape or portrait."""
    if width >= height:
        return "Landscape"
    return "Portrait"

def extract_resolution_key(resolution):
    """Extract the first numeric value (A) from 'AxB' format for sorting."""
    match = re.match(r"(\d+)", resolution)
    return int(match.group(1)) if match else float('inf')

def parse_resolution(resolution):
    """Extract width and height from 'AxB' resolution format."""
    match = re.match(r"(\d+)x(\d+)", resolution)
    if match:
        return map(int, match.groups())
    return None, None

def load_existing_data(filepath):
    """Load existing data from a file and separate special symbols (@, #)."""
    data = {}

    if not os.path.exists(filepath):
        return data

    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            symbol = ""
            value = line
            if line[0] in {"@", "#"}:
                symbol = line[0]
                value = line[1:]
            data[value] = symbol  # Store value with its associated symbol

    return data

def save_sorted_resolutions(filepath, data):
    """Sort resolutions numerically by A in AxB and save to file."""
    sorted_values = sorted(data.keys(), key=extract_resolution_key)
    with open(filepath, "w", encoding="utf-8") as file:
        for value in sorted_values:
            file.write(f"{data[value]}{value}\n")  # Restore symbol before value

def save_sorted_codecs(filepath, data):
    """Sort codecs alphabetically and save to file."""
    sorted_values = sorted(data.keys(), key=lambda x: x.lower())
    with open(filepath, "w", encoding="utf-8") as file:
        for value in sorted_values:
            file.write(f"{data[value]}{value}\n")

def normalize_codec(codec):
    """Normalize codecs into categories."""
    if codec.startswith("av01."):
        return "av01"
    elif codec.startswith("avc1."):
        return "avc1"
    elif codec.startswith("vp09."):
        return "vp09"
    elif codec == "vp9":
        return "vp09"
    return codec

def process_json(json_file):
    """Extract and update resolution and codec files."""
    metadata = load_json(json_file)

    if "formats" not in metadata:
        print("Error: 'formats' data missing in JSON file.")
        sys.exit(1)

    resolutions = set()
    codecs = set()
    highest_resolution = (0, 0)

    for fmt in metadata["formats"]:
        video_ext = fmt.get("video_ext", "none")
        if video_ext == "none":
            continue  # Skip this format

        resolution = fmt.get("resolution", "").strip()
        vcodec = fmt.get("vcodec", "").strip()
        width = fmt.get("width", 0) or 0
        height = fmt.get("height", 0) or 0

        if resolution:
            resolutions.add(resolution)
            if width * height > highest_resolution[0] * highest_resolution[1]:
                highest_resolution = (width, height)

        if vcodec:
            normalized_codec = normalize_codec(vcodec)
            codecs.add(normalized_codec)

    orientation = determine_orientation(*highest_resolution)
    log_debug(f"Video Orientation: {orientation}")

    resolution_file = RES_LANDSCAPE_FILE if orientation == "Landscape" else RES_PORTRAIT_FILE
    existing_resolutions = load_existing_data(resolution_file)
    existing_codecs = load_existing_data(VIDEO_CODEC_FILE)

    # Update resolution and codec files
    for res in resolutions:
        if res not in existing_resolutions:
            existing_resolutions[res] = ""

    for codec in codecs:
        if codec not in existing_codecs:
            existing_codecs[codec] = ""

    save_sorted_resolutions(resolution_file, existing_resolutions)
    save_sorted_codecs(VIDEO_CODEC_FILE, existing_codecs)

    # print(f"Updated {resolution_file} and {VIDEO_CODEC_FILE}")

def main():
    """Main execution."""
    json_file = validate_input()
    process_json(json_file)

if __name__ == "__main__":
    main()
