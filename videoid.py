import sys
import os
import json
import re

# File paths for storing resolutions and codecs
RES_LANDSCAPE_FILE = "docs/video_resolutions_landscape.txt"
RES_PORTRAIT_FILE = "docs/video_resolutions_portrait.txt"
VIDEO_CODEC_FILE = "docs/video_codecs.txt"

def is_json_file(filename):
    """Check if the given filename is a JSON file."""
    return filename.lower().endswith(".json")

def load_existing_data(filepath):
    """Load existing data from a file and separate special symbols."""
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

def extract_resolution_key(resolution):
    """Extract the first numeric value (A) from 'AxB' format for sorting."""
    match = re.match(r"(\d+)", resolution)  # Extract the first number
    return int(match.group(1)) if match else float('inf')  # Default to infinity if no number found

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
    return codec  # Return original if no match

def parse_resolution(resolution):
    """Extract width and height from 'AxB' resolution format."""
    match = re.match(r"(\d+)x(\d+)", resolution)
    if match:
        width, height = map(int, match.groups())
        return width, height
    return None, None  # Return None if format is incorrect

def determine_orientation(highest_resolution):
    """Determine whether the video is landscape or portrait."""
    width, height = parse_resolution(highest_resolution)
    if width is not None and height is not None:
        return "Landscape" if width >= height else "Portrait"
    return "Unknown"

def save_sorted_resolutions(filepath, data):
    """Sort resolutions numerically by A in AxB and save to file."""
    sorted_values = sorted(data.keys(), key=extract_resolution_key)
    with open(filepath, "w", encoding="utf-8") as file:
        for value in sorted_values:
            file.write(f"{data[value]}{value}\n")  # Restore symbol before value

def save_sorted_codecs(filepath, data):
    """Sort codecs alphabetically and save to file."""
    sorted_values = sorted(data.keys(), key=lambda x: x.lower())  # Case-insensitive sorting
    with open(filepath, "w", encoding="utf-8") as file:
        for value in sorted_values:
            file.write(f"{data[value]}{value}\n")  # Restore symbol before value

def process_json(json_file):
    """Read JSON, extract required data, update resolution & codec files, and determine orientation."""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            metadata = json.load(file)
    except Exception as e:
        print(f"Error: Failed to read JSON file '{json_file}'. Reason: {e}")
        sys.exit(1)

    if "formats" not in metadata:
        print("Error: 'formats' data missing in JSON file.")
        sys.exit(1)

    highest_resolution = None
    codec_set = set()
    resolution_set = set()

    for format_data in metadata["formats"]:
        video_ext = format_data.get("video_ext", "none")

        if video_ext == "none":
            continue  # Skip this format

        resolution = format_data.get("resolution", "").strip()
        vcodec = format_data.get("vcodec", "").strip()
        vcodec_normalized = normalize_codec(vcodec)

        if resolution:
            resolution_set.add(resolution)

            # Track the highest resolution
            if highest_resolution is None or extract_resolution_key(resolution) > extract_resolution_key(highest_resolution):
                highest_resolution = resolution

        if vcodec_normalized:
            codec_set.add(vcodec_normalized)

    # Determine video orientation
    orientation = determine_orientation(highest_resolution) if highest_resolution else "Unknown"
    print(f"Video Orientation: {orientation}")

    # Load existing resolution data
    res_file = RES_LANDSCAPE_FILE if orientation == "Landscape" else RES_PORTRAIT_FILE
    existing_resolutions = load_existing_data(res_file)

    # Update resolutions
    for res in resolution_set:
        if res not in existing_resolutions:
            existing_resolutions[res] = ""  # No special symbol by default

    # Save updated resolutions
    save_sorted_resolutions(res_file, existing_resolutions)
    print(f"Updated {res_file}")

    # Load existing codec data
    existing_codecs = load_existing_data(VIDEO_CODEC_FILE)

    # Update codecs
    for codec in codec_set:
        if codec not in existing_codecs:
            existing_codecs[codec] = ""

    # Save updated codecs
    save_sorted_codecs(VIDEO_CODEC_FILE, existing_codecs)
    print(f"Updated {VIDEO_CODEC_FILE}")

def main():
    """Process the given JSON file."""
    if len(sys.argv) < 2:
        print("Error: No JSON file provided. Usage: videoid.py <jsonfile>")
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' does not exist.")
        sys.exit(1)

    if not is_json_file(json_file):
        print(f"Error: File '{json_file}' is not a JSON file.")
        sys.exit(1)

    process_json(json_file)

if __name__ == "__main__":
    main()
