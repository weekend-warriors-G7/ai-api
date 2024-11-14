import os
from imgur import save_imgur_image
from flask import Flask, request, jsonify
from config import CACHE_PATH

app = Flask(__name__)

@app.route('/compare', methods=['POST'])
def compare():
    # Check request for sanity.
    data = request.get_json()
    if data == None:
        return jsonify('No JSON data specified.')
    if data["first"] == None or data["second"] == None:
        return jsonify("No first or second image links specified.")
    if type(data["first"]) != str or type(data["second"]) != str:
        return jsonify("First and second must be strings.")

    # Make cache dir if it doesnt exist.
    os.makedirs(CACHE_PATH, exist_ok=True) 
    
    # Let's get the images and cry if we don't.
    try:
        save_imgur_image(data["first"], CACHE_PATH)
        save_imgur_image(data["second"], CACHE_PATH)
    except Exception as error:
        return jsonify(error.__str__())

    return jsonify(data)