import sys
import os

# File path for audio codecs
AUDIO_CODEC_FILE = "docs/audio_codecs.txt"

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

def load_codecs():
    """Loads codec lines from the file, preserving order and markers."""
    if not os.path.exists(AUDIO_CODEC_FILE):
        log_debug(f"File '{AUDIO_CODEC_FILE}' does not exist. Skipping.")
        return []

    with open(AUDIO_CODEC_FILE, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def save_codecs(lines):
    """Writes the codec lines back to the file."""
    with open(AUDIO_CODEC_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")

def update_codecs():
    """Ensure `mp4a` is the highest priority codec and `opus` is second while preserving order."""
    codecs = load_codecs()
    if not codecs:
        return

    log_debug(f"Initial codecs: {codecs}")

    codec_map = {}  # Stores markers for each codec
    ordered_codecs = []  # Stores codecs in order

    for line in codecs:
        marker = ""
        codec = line

        if line.startswith("@") or line.startswith("#"):
            marker, codec = line[0], line[1:]

        codec_map[codec] = marker  # Preserve marker
        ordered_codecs.append(codec)

    updated = False

    # Check if @ or # is present
    has_at_mp4a = codec_map.get("mp4a") == "@"
    has_hash_mp4a = codec_map.get("mp4a") == "#"
    has_at_opus = codec_map.get("opus") == "@"
    has_hash_opus = codec_map.get("opus") == "#"

    if has_hash_mp4a and not has_at_opus:
        codec_map["opus"] = "@"
        updated = True

    if has_hash_opus and not has_at_mp4a:
        codec_map["mp4a"] = "@"
        updated = True

    # If no markers exist, add @mp4a and #opus
    if not has_at_mp4a and not has_hash_mp4a and not has_at_opus and not has_hash_opus:
        codec_map["mp4a"] = "@"
        codec_map["opus"] = "#"
        updated = True

    if updated:
        updated_codecs = [f"{codec_map.get(c, '')}{c}" for c in ordered_codecs]
        save_codecs(updated_codecs)
        log_debug(f"Updated codecs: {updated_codecs}")
    else:
        log_debug("No changes needed.")

def main():
    """Main execution."""
    validate_input()
    update_codecs()

if __name__ == "__main__":
    main()
