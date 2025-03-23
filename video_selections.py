import sys
import os

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
    """Validate command-line arguments and check if debug mode is enabled."""
    global DEBUG_MODE

    if "-d" in sys.argv:
        DEBUG_MODE = True
        sys.argv.remove("-d")  # Remove debug flag from arguments

def load_resolutions(file_path):
    """Load resolutions from a file and return them as a list."""
    if not os.path.exists(file_path):
        log_debug(f"File '{file_path}' does not exist. Skipping.")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def save_resolutions(file_path, resolutions):
    """Save resolutions back to the file, ensuring priority markers are preserved."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(resolutions) + "\n")

def ensure_priority_markers(resolutions):
    """Ensure `@` (mandatory) and `#` (optional) exist in the resolution list."""
    has_at = any(res.startswith("@") for res in resolutions)

    if has_at:
        log_debug("Priority markers found. No changes needed.")
        return resolutions  # No changes needed

    # Select the highest resolution (last item in sorted list) and mark it with `@`
    if resolutions:
        resolutions[-1] = "@" + resolutions[-1]
        log_debug(f"No priority markers found. Assigned '@' to: {resolutions[-1]}")
    return resolutions

def update_codecs():
    """Ensure `vp09` is the highest priority codec and `av01` is second."""
    if not os.path.exists(VIDEO_CODEC_FILE):
        log_debug(f"File '{VIDEO_CODEC_FILE}' does not exist. Skipping.")
        return

    with open(VIDEO_CODEC_FILE, "r", encoding="utf-8") as file:
        codecs = [line.strip() for line in file if line.strip()]

    # Extract priority markers before sorting
    priority_map = {}
    cleaned_codecs = []
    
    for line in codecs:
        marker = ""
        codec_name = line

        if line.startswith("@") or line.startswith("#"):
            marker, codec_name = line[0], line[1:]

        priority_map[codec_name] = marker  # Preserve marker
        cleaned_codecs.append(codec_name)

    # Sort without losing priority markers
    sorted_codecs = sorted(set(cleaned_codecs))

    # Reapply existing priority markers
    updated_codecs = []
    for codec in sorted_codecs:
        if codec in priority_map:
            updated_codecs.append(priority_map[codec] + codec)
        else:
            updated_codecs.append(codec)

    # Determine if `@` and `#` need to be assigned
    has_at = any(c.startswith("@") for c in updated_codecs)
    has_hash = any(c.startswith("#") for c in updated_codecs)

    vp09_index = updated_codecs.index("vp09") if "vp09" in updated_codecs else None
    av01_index = updated_codecs.index("av01") if "av01" in updated_codecs else None

    if not has_at and not has_hash:
        # If neither `@` nor `#` is present, add `@vp09` and `#av01`
        if vp09_index is not None:
            updated_codecs[vp09_index] = "@vp09"
        if av01_index is not None:
            updated_codecs[av01_index] = "#av01"

    elif not has_at and has_hash:
        # If `#` is present but `@` is missing
        if vp09_index is not None and updated_codecs[vp09_index].startswith("#"):
            updated_codecs[av01_index] = "@av01"  # Convert `#vp09` → `@av01`
        elif av01_index is not None and updated_codecs[av01_index].startswith("#"):
            updated_codecs[vp09_index] = "@vp09"  # Convert `#av01` → `@vp09`

    # If `@` is present but `#` is missing, or both are present, do nothing

    with open(VIDEO_CODEC_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(updated_codecs) + "\n")

    log_debug(f"Updated codec priorities: {', '.join(updated_codecs)}")

def process_selections():
    """Process resolutions and codecs selection."""
    landscape_res = load_resolutions(RES_LANDSCAPE_FILE)
    portrait_res = load_resolutions(RES_PORTRAIT_FILE)

    # Update resolution files with priority markers
    if landscape_res:
        landscape_res = ensure_priority_markers(landscape_res)
        save_resolutions(RES_LANDSCAPE_FILE, landscape_res)

    if portrait_res:
        portrait_res = ensure_priority_markers(portrait_res)
        save_resolutions(RES_PORTRAIT_FILE, portrait_res)

    # Update codec priorities
    update_codecs()

    # print("Updated resolutions and codecs successfully.")

def main():
    """Main execution."""
    validate_input()
    process_selections()

if __name__ == "__main__":
    main()
