import os
import sqlite3
from resnet_model.run_model import get_similarity
from imgur import save_imgur_image, get_filename_and_extension
from flask import Flask, request, jsonify
from config import CACHE_PATH, APP_VERSION, DEBUG

def init_db():
    db_path = os.path.join(CACHE_PATH, 'comparisons.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the version table exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS version (
        app_version TEXT
    )
    ''')
    cursor.execute('SELECT app_version FROM version')
    row = cursor.fetchone()

    if row:
        current_version = row[0]
        if current_version != APP_VERSION:
            # Version mismatch, reset the database
            cursor.execute('DROP TABLE IF EXISTS comparisons')
            cursor.execute('CREATE TABLE comparisons (source TEXT, target TEXT, result REAL, PRIMARY KEY (source, target))')
            cursor.execute('UPDATE version SET app_version = ?', (APP_VERSION,))
    else:
        # No version set, initialize the database
        cursor.execute('CREATE TABLE IF NOT EXISTS comparisons (source TEXT, target TEXT, result REAL, PRIMARY KEY (source, target))')
        cursor.execute('INSERT INTO version (app_version) VALUES (?)', (APP_VERSION,))
    
    conn.commit()
    conn.close()

def compare_image(first_path: str, second_path_link: str):
    db_path = os.path.join(CACHE_PATH, 'comparisons.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the comparison result is already in the database
    cursor.execute('SELECT result FROM comparisons WHERE source = ? AND target = ?', (first_path, second_path_link))
    row = cursor.fetchone()

    if row:
        result = row[0]
    else:
        # Perform the comparison
        first_path_local = save_imgur_image(first_path, CACHE_PATH)
        second_path_local = save_imgur_image(second_path_link, CACHE_PATH)
        result, time = get_similarity(first_path_local, second_path_local)
        
        # Save the result in the database
        cursor.execute('INSERT INTO comparisons (source, target, result) VALUES (?, ?, ?)', (first_path, second_path_link, result))
        conn.commit()

    conn.close()
    return second_path_link, result


app = Flask(__name__)

os.makedirs(CACHE_PATH, exist_ok=True)
init_db()

@app.route('/compare', methods=['POST'])
def compare():
    # Check request for sanity.
    data = request.get_json()
    if data is None:
        return jsonify('No JSON data specified.')
    if data["source"] is None or data["others"] is None:
        return jsonify("No source or other image links specified.")
    if type(data["source"]) != str or type(data["others"]) != list:
        return jsonify("First and second must be strings.")
    for element in data["others"]:
        if type(element) != str:
            return jsonify("A others' value was not a link.")

    # Let's get the images and ignore the erroring images if something is wrong.
    final_result = []
    for otherImage in data["others"]:
        try:
            identifier, result = compare_image(data["source"], otherImage)
            element = dict()
            element["id"] = identifier
            element["confidence"] = result 
            final_result.append(element)
        except Exception as error:
            pass

    final_result.sort(key=lambda x: x["confidence"], reverse=True)
    return jsonify(final_result)

if __name__ == "__main__":
    app.run(debug=DEBUG)