import time
import os

def generate_unique_filename():
    """Generate a unique temporary filename based on system time in milliseconds."""
    while True:
        timestamp = str(int(time.time() * 1000))[-8:]  # Get last 8 digits of milliseconds
        filename = f".{timestamp}.json"

        if not os.path.exists(filename):
            return filename  # Return the unique filename

# If executed directly, print the generated filename for testing
if __name__ == "__main__":
    print(generate_unique_filename())
