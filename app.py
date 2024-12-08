import os
from resnet_model.run_model import get_similarity
from imgur import save_imgur_image, get_filename_and_extension
from flask import Flask, request, jsonify
from config import CACHE_PATH

app = Flask(__name__)

def compare_image(first_path: str, second_path_link: str):
    first_path = save_imgur_image(first_path, CACHE_PATH)       #
    second_path = save_imgur_image(second_path_link, CACHE_PATH)     # Get local path for the imgur paths.
    result, time = get_similarity(first_path, second_path)
    _, output, _ = get_filename_and_extension(second_path)
    return second_path_link, result

@app.route('/compare', methods=['POST'])
def compare():
    # Check request for sanity.
    data = request.get_json()
    if data == None:
        return jsonify('No JSON data specified.')
    if data["source"] == None or data["others"] == None:
        return jsonify("No source or other image links specified.")
    if type(data["source"]) != str or type(data["others"]) != list:
        return jsonify("First and second must be strings.")
    for element in data["others"]:
        if type(element) != str:
            return jsonify("A others' value was not a link.")

    # Make cache dir if it doesnt exist.
    os.makedirs(CACHE_PATH, exist_ok=True) 
    
    # Let's get the images and ignore the erroring images if something is wrong.
    final_result = []
    for otherImage in data["others"]:
        try:
            identifier, result = compare_image(data["source"], otherImage)
            element = dict()
            element["id"] = identifier
            element["confidence"] = result 
            final_result.append(element)
        except error as Exception:
            pass

    final_result.sort(key=lambda x: x["confidence"], reverse=True)
    return jsonify(final_result)


if __name__ == "__main__":
    app.run(debug=True)