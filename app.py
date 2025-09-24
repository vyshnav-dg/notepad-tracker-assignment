import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from git import Repo

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/read-file', methods=['POST'])
def read_file():
    data = request.get_json()
    path = data.get('path')
    path = path.removeprefix('"').removesuffix('"')

    if not path:
        return jsonify({"error": "No path provided"}), 400

    abs_path = os.path.abspath(path)
    print(abs_path)
    if not os.path.exists(abs_path):
        with open(f"{abs_path}", "x"):
            # Create the file if it doesnt exist
            pass
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/file-updated', methods=["POST"])
def update_file():
    try:
        data = request.get_json()
        path = data.get("path").removeprefix('"').removesuffix('"')
        content = data.get("content")
        dirname = os.path.dirname(os.path.abspath(path))
        filename = os.path.basename(os.path.abspath(path))

        with open(path, "w") as f:
            f.write(content)
            print("Written to file")
        repo = Repo.init(dirname)
        print("Initialized git")
        repo.index.add([filename])
        print(f"Added {filename} to staging")
        repo.index.commit(f"{filename} - {datetime.now()}")
        print(f"Commit added")
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500