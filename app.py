from flask import Flask, render_template, request, send_file, abort
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
import database
from datetime import datetime

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100*1024*1024

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
         "errors/error.html",
         error_code = 404,
         error_type = "File Not Found",
         message = "The requested file could not be found."
    ), 404

@app.errorhandler(413)
def request_too_large(error):
     return render_template(
          "errors/error.html",
          error_code = 413,
          error_type = "File size too large",
          message = "The maximum upload size is 100 MB."
     ), 413

@app.errorhandler(500)
def internal_server_error(error):
     return render_template(
          "errors/error.html",
          error_code = 500,
          error_type = "Internal Server Error",
          message = "Something went wrong while processing your request."
     ), 500

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


''' Cleanup function: To register a callback, whenever the application is torn down, call database.close_db() '''
app.teardown_appcontext(database.close_db)      

with app.app_context():
    database.init_db()


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
    failed_filenames = []
    uploaded_files = request.files.getlist("file")
    if len(uploaded_files)>10:
            return render_template(
                "errors/error.html",
                error_code=400,
                error_type="File Limit Exceeded",
                message=f"Please upload upto 10 files at a time."
            ), 400


    if not uploaded_files:
        return render_template(
             "errors/error.html",
             error_code = 400,
             error_type = "No files uploaded",
             message = "Please select one file to upload."
        ), 400
    for uploaded_file in uploaded_files:
        if not uploaded_file.filename:
            continue

        unique_id = uuid.uuid4()
        original_filename = secure_filename(uploaded_file.filename)
        stored_filename = f"{unique_id}_{original_filename}"
        destination = UPLOAD_FOLDER / stored_filename

        try:
            upload_time = datetime.now().isoformat()
            uploaded_file.save(destination)
        
            size = destination.stat().st_size
            database.create_file(str(unique_id),
                                original_filename,
                                stored_filename,
                                upload_time,
                                size)    
            uploaded_filenames.append(original_filename)
        except Exception:
            if(destination.isfile()):
                destination.unlink()
            failed_filenames.append(original_filename)

    if not uploaded_filenames:
        return render_template(
                     "errors/error.html",
                     error_code = 400,
                     error_type = "No files uploaded",
                     message = "Please select one file to upload."
                ), 400

    return render_template(
                            "success.html",
                            uploaded_files = uploaded_filenames,
                            failed_files = failed_filenames
                        )

@app.route("/download/<stored_filename>", methods = ["GET"])
def download(stored_filename):

    file = database.get_file(stored_filename)
    if file is None:
        abort(404)

    destination = UPLOAD_FOLDER / file["stored_filename"]
    if not destination.is_file():
            abort(404)

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
    except Exception:
            abort(500)

    
    return render_template("deleted.html", f = file["original_filename"])
    

if __name__ == "__main__":
    app.run(debug=True)