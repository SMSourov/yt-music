import sys
import os

# File path for audio format notes
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

def load_format_notes():
    """Loads format note lines from the file, preserving order and markers."""
    if not os.path.exists(AUDIO_FORMAT_NOTE_FILE):
        log_debug(f"File '{AUDIO_FORMAT_NOTE_FILE}' does not exist. Skipping.")
        return []

    with open(AUDIO_FORMAT_NOTE_FILE, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def save_format_notes(lines):
    """Writes the format note lines back to the file."""
    with open(AUDIO_FORMAT_NOTE_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")

def update_format_notes():
    """Ensure `medium` is the highest priority and `medium, DRC` is second while preserving order."""
    format_notes = load_format_notes()
    if not format_notes:
        return

    log_debug(f"Initial format notes: {format_notes}")

    note_map = {}  # Stores markers for each format note
    ordered_notes = []  # Stores format notes in order

    for line in format_notes:
        marker = ""
        note = line

        if line.startswith("@") or line.startswith("#"):
            marker, note = line[0], line[1:]

        note_map[note] = marker  # Preserve marker
        ordered_notes.append(note)

    updated = False

    # Check if @ or # is present
    has_at_medium = note_map.get("medium") == "@"
    has_hash_medium = note_map.get("medium") == "#"
    has_at_medium_drc = note_map.get("medium, DRC") == "@"
    has_hash_medium_drc = note_map.get("medium, DRC") == "#"

    if has_hash_medium and not has_at_medium_drc:
        note_map["medium, DRC"] = "@"
        updated = True

    if has_hash_medium_drc and not has_at_medium:
        note_map["medium"] = "@"
        updated = True

    # If no markers exist, add @medium and #medium, DRC
    if not has_at_medium and not has_hash_medium and not has_at_medium_drc and not has_hash_medium_drc:
        note_map["medium"] = "@"
        note_map["medium, DRC"] = "#"
        updated = True

    if updated:
        updated_notes = [f"{note_map.get(n, '')}{n}" for n in ordered_notes]
        save_format_notes(updated_notes)
        log_debug(f"Updated format notes: {updated_notes}")
    else:
        log_debug("No changes needed.")

def main():
    """Main execution."""
    validate_input()
    update_format_notes()

if __name__ == "__main__":
    main()
