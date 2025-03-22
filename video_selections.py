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

    # Ensure priority markers for `vp09` (@) and `av01` (#)
    new_codecs = []
    found_vp09 = found_av01 = False

    for codec in codecs:
        clean_codec = codec.lstrip("@#")  # Remove existing markers

        if clean_codec == "vp09":
            new_codecs.append("@" + clean_codec)
            found_vp09 = True
        elif clean_codec == "av01":
            new_codecs.append("#" + clean_codec)
            found_av01 = True
        else:
            new_codecs.append(clean_codec)

    # If `vp09` wasn't found, insert it at the top with `@`
    if not found_vp09:
        new_codecs.insert(0, "@vp09")
    
    # If `av01` wasn't found, insert it after `vp09` with `#`
    if not found_av01:
        new_codecs.insert(1, "#av01")

    with open(VIDEO_CODEC_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(new_codecs) + "\n")

    log_debug(f"Updated codec priorities: {', '.join(new_codecs)}")

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

    print("Updated resolutions and codecs successfully.")

def main():
    """Main execution."""
    validate_input()
    process_selections()

if __name__ == "__main__":
    main()
