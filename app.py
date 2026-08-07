from flask import Flask, render_template, request, send_file, abort
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
import database
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

with app.app_context():
    database.init_db()

''' Cleanup function: To register a callback, whenever the application is torn down, call database.close_db() '''
app.teardown_appcontext(database.close_db)      

@app.route("/")
def home():
    files = database.list_files()

    return render_template(
        "index.html",
        files=files
        )

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
        upload_time = datetime.now().isoformat()
        size = destination.stat().st_size
        
        database.create_file(str(unique_id),
                            original_filename,
                            stored_filename,
                            upload_time,
                            size)    

    if not uploaded_filenames:
        return "No files uploaded."

    return render_template(
                            "success.html",
                            files = uploaded_filenames
                        )

@app.route("/download/<stored_filename>", methods = ["GET"])
def download(stored_filename):

    file = database.get_file(stored_filename)
    if not file:
        abort(404)

    destination = UPLOAD_FOLDER / file["stored_filename"]
    return send_file(destination,
                     as_attachment=True,
                     download_name=file["original_filename"]
                    )

@app.route("/delete/<stored_filename>", methods=["POST"])
def delete(stored_filename):

    file = database.get_file(stored_filename)
    if file is None:
        abort(404)
    
    destination = UPLOAD_FOLDER / file["stored_filename"]
    if not destination.is_file():
        abort(404)
    try:
        destination.unlink()
        database.delete_file(stored_filename)
    except Exception as e:
        return f"Deletion failed due to {e}"
    
    return render_template("deleted.html", f = file["original_filename"])
    


if __name__ == "__main__":
    app.run(debug=True)