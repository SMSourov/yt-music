import sys
import os
import json
import re

VIDEO_RES_FILE = "docs/video_resolutions.txt"
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
    """Read JSON, extract required data, and update resolution & codec files."""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            metadata = json.load(file)
    except Exception as e:
        print(f"Error: Failed to read JSON file '{json_file}'. Reason: {e}")
        sys.exit(1)

    if "formats" not in metadata:
        print("Error: 'formats' data missing in JSON file.")
        sys.exit(1)

    existing_resolutions = load_existing_data(VIDEO_RES_FILE)
    existing_codecs = load_existing_data(VIDEO_CODEC_FILE)

    for format_data in metadata["formats"]:
        video_ext = format_data.get("video_ext", "none")

        if video_ext == "none":
            continue  # Skip this format

        resolution = format_data.get("resolution", "").strip()
        vcodec = format_data.get("vcodec", "").strip()
        vcodec_normalized = normalize_codec(vcodec)

        if resolution and resolution not in existing_resolutions:
            existing_resolutions[resolution] = ""  # No special symbol by default

        if vcodec_normalized and vcodec_normalized not in existing_codecs:
            existing_codecs[vcodec_normalized] = ""  # No special symbol by default

    # Save sorted resolutions and codecs
    save_sorted_resolutions(VIDEO_RES_FILE, existing_resolutions)
    save_sorted_codecs(VIDEO_CODEC_FILE, existing_codecs)

    print(f"Updated {VIDEO_RES_FILE} and {VIDEO_CODEC_FILE}")

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
