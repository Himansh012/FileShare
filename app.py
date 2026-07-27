from flask import Flask, render_template, request, send_file, abort
from pathlib import Path
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.route("/")
def home():
    return render_template(
                            "index.html",
                            files = [
                                file 
                                for file in UPLOAD_FOLDER.iterdir()
                                  if file.is_file() and not file.name.startswith(".")]
                           )

@app.route("/upload", methods = ["POST"])
def upload():
    uploaded_file_list = []
    uploaded_files = request.files.getlist("file")
    if not uploaded_files:
        return "No files uploaded"
    for uploaded_file in uploaded_files:
        if not uploaded_file.filename:
            continue
        
        filename = secure_filename(uploaded_file.filename)
        filename = f"{int(time.time())}_{filename}"

        destination = UPLOAD_FOLDER / filename
        uploaded_file.save(destination)
        uploaded_file_list.append(uploaded_file.filename)

    return render_template(
                            "success.html",
                            files = uploaded_file_list
                        )

@app.route("/download/<filename>", methods = ["GET"])
def download(filename):
    destination = UPLOAD_FOLDER / filename
    if not destination.is_file():
        abort(404)
    return send_file(destination,
                     as_attachment=True)



if __name__ == "__main__":
    app.run(debug=True)