from flask import Flask, render_template, request, send_file, abort
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.route("/")
def home():

    files = []

    for file in UPLOAD_FOLDER.iterdir():
        if not file.is_file() or file.name.startswith("."):
            continue

        original_file = file.name.split("_",1)[1]

        files.append({
            "stored_name":file.name,
            "original_name":original_file
        })
        
    return render_template("index.html",files=files)

@app.route("/upload", methods = ["POST"])
def upload():
    uploaded_filenames = []
    uploaded_files = request.files.getlist("file")
    if not uploaded_files:
        return "No files uploaded"
    for uploaded_file in uploaded_files:
        if not uploaded_file.filename:
            continue

        unique_id = uuid.uuid4()
        original_filename = secure_filename(uploaded_file.filename)
        stored_filename = f"{unique_id}_{original_filename}"

        destination = UPLOAD_FOLDER / stored_filename
        uploaded_file.save(destination)
        uploaded_filenames.append(original_filename)

    if not uploaded_filenames:
        return "No files uploaded."
    return render_template(
                            "success.html",
                            files = uploaded_filenames
                        )

@app.route("/download/<filename>", methods = ["GET"])
def download(filename):

    destination = UPLOAD_FOLDER / filename

    original_name = destination.name.split("_",1)[1]

    if not destination.is_file():
        abort(404)
    return send_file(destination,
                     as_attachment=True,
                     download_name=original_name
                     )

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    destination = UPLOAD_FOLDER / filename
    original_file = filename.split("_",1)[1]

    if not destination.is_file():
        abort(404)
    try:
        destination.unlink()
    except Exception as e:
        return f"Deletion failed due to {e}"
    
    return render_template("deleted.html", f = original_file)
    


if __name__ == "__main__":
    app.run(debug=True)