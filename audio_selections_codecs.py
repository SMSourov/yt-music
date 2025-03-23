import sys
import os

# File path for audio codecs
AUDIO_CODEC_FILE = "docs/audio_codecs.txt"

# Global debug flag
DEBUG_MODE = False

def log_debug(message):
    """Print debug messages only if debug mode is enabled."""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def validate_input():
    """Validate command-line arguments and enable debug mode if '-d' is provided."""
    global DEBUG_MODE
    if "-d" in sys.argv:
        DEBUG_MODE = True
        sys.argv.remove("-d")

def load_codecs(file_path):
    """Load codec lines from the file, preserving order and markers."""
    if not os.path.exists(file_path):
        log_debug(f"File '{file_path}' does not exist.")
        return []
    
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def save_codecs(file_path, lines):
    """Write the codec lines back to the file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")

def update_codec_priorities():
    """Ensure correct priority markers in AUDIO_CODEC_FILE without removing existing ones."""
    lines = load_codecs(AUDIO_CODEC_FILE)
    if not lines:
        log_debug("No codecs found.")
        return

    log_debug(f"Initial lines: {lines}")

    has_at = any(line.startswith("@") for line in lines)
    has_hash = any(line.startswith("#") for line in lines)

    # Preserve order and existing markers
    codec_map = {}
    ordered_codecs = []
    
    for line in lines:
        marker = ""
        codec = line

        if line.startswith("@") or line.startswith("#"):
            marker, codec = line[0], line[1:]

        codec_map[codec] = marker
        ordered_codecs.append(codec)

    log_debug(f"Before processing: {codec_map}")

    updated = False

    if has_at and has_hash:
        log_debug("Both '@' and '#' exist. No changes needed.")
        return

    if not has_at and not has_hash:
        # No '@' or '#' present → Add '@medium' and '#low'
        if "medium" in codec_map and codec_map["medium"] == "":
            codec_map["medium"] = "@"
            updated = True
        if "low" in codec_map and codec_map["low"] == "":
            codec_map["low"] = "#"
            updated = True

    elif not has_at and has_hash:
        # If `#` exists but `@` is missing
        for codec, marker in codec_map.items():
            if marker == "#":
                if codec != "medium":
                    if "medium" in codec_map and codec_map["medium"] == "":
                        codec_map["medium"] = "@"
                        updated = True
                        break
                elif codec == "medium":
                    if "low" in codec_map and codec_map["low"] == "":
                        codec_map["low"] = "@"
                        updated = True
                        break

    log_debug(f"After processing: {codec_map}")

    if updated:
        updated_lines = [f"{codec_map.get(codec, '')}{codec}" for codec in ordered_codecs]
        save_codecs(AUDIO_CODEC_FILE, updated_lines)
        print("Updated audio codecs successfully.")
    else:
        log_debug("No changes needed.")

def main():
    validate_input()
    update_codec_priorities()

if __name__ == "__main__":
    main()
