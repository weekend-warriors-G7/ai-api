import re
import subprocess
import os

def get_filename_and_extension(url):
    pattern = r"/([^/]+)(\.[^.]+)$"
    match = re.search(pattern, url)
    if match:
        filename_without_extension = match.group(1)
        file_extension = match.group(2)
        filename = filename_without_extension + file_extension
        return filename, filename_without_extension, file_extension
    else:
        return None

def save_imgur_image(link: str, CACHE_PATH: str):
    filename_info = get_filename_and_extension(link)
    if filename_info is None:
        raise Exception("Invalid URL: Unable to extract filename and extension.")

    filename, filename_without_extension, file_extension = filename_info
    save_path = os.path.join(CACHE_PATH, filename)

    # If file exists do not download again.
    if os.path.exists(save_path):
        return save_path

    # Execute curl to download the image
    try:
        result = subprocess.run(
            ["curl", "-L", "-o", save_path, link],
            check=True,
            text=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error occurred while downloading the image: {e.stderr}")

    return save_path
