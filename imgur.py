import re
import requests

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
    filename = get_filename_and_extension(link)

    # Make request to the image.
    requestData = requests.get(link, stream=True)

    # Something happend while getting shit idk.
    if requestData.status_code != 200:
        raise Exception("Error occured while making Imgur request at link (" + str(link) + ")! Error code: " + str(requestData.status_code))

    # Save the image.
    with open(CACHE_PATH + filename, 'wb') as handler:
        for chunk in response.iter_content(1024):
            handler.write(chunk)