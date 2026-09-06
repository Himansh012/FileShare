from flask import Blueprint, render_template, request, send_file, abort
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
from pathlib import Path

import database
import config
import helper

routes = Blueprint("routes", __name__)

@routes.route("/")
def home():
    files = database.list_files()
    uploaded_folder = [ufile.name for ufile in config.UPLOAD_FOLDER.iterdir() if ufile]
    
    for file in files:
        if file["stored_filename"] not in uploaded_folder:
            database.delete_file(file["stored_filename"])
            files.remove(file)
    return render_template(
        "index.html",
        files=files,
        format_size = helper.format_size
        )

@routes.route("/upload", methods = ["POST"])
def upload():
    uploaded_filenames = []
    failed_filenames = {}
    warned_filenames = {}
    uploaded_files = request.files.getlist("file")
    
    uploaded_files = [file for file 
                      in uploaded_files 
                      if file.filename]
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
        
        extension = Path(uploaded_file.filename).suffix.lower()
        if extension not in config.ALLOWED_FILE_TYPES:
            failed_filenames[uploaded_file.filename] = "file type not allowed"
            continue
        file_mime = uploaded_file.mimetype 
        if file_mime != config.ALLOWED_FILE_TYPES[extension]:
            failed_filenames[uploaded_file.filename] = "invalid file MIME Type"
            continue

        unique_id = uuid.uuid4()
        original_filename = secure_filename(uploaded_file.filename)
        original_filename = helper.file_name_incrementer(original_filename)
        stored_filename = f"{unique_id}_{original_filename}"
        destination = config.UPLOAD_FOLDER / stored_filename

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

            if size==0:
                 warned_filenames[uploaded_file.filename] = "File has no content, check the upload carefully"

        except Exception:
            if(destination.is_file()):
                destination.unlink()
            failed_filenames[original_filename] = "File Failed due to some exception"

    if len(uploaded_filenames)==0 and len(failed_filenames)>0:
        return render_template(
                                "errors/failed_upload.html",
                                error_code = 415,
                                error_type = "Unsupported File Type",
                                failed_filenames = failed_filenames
                            )
    return render_template(
                            "success.html",
                            uploaded_files = uploaded_filenames,
                            failed_files = failed_filenames,
                            warned_files = warned_filenames
                        )

@routes.route("/download/<stored_filename>", methods = ["GET"])
def download(stored_filename):

    file = database.get_file(stored_filename)
    if file is None:
        abort(404)

    destination = config.UPLOAD_FOLDER / file["stored_filename"]
    if not destination.is_file():
            abort(404)

    return send_file(destination,
                     as_attachment=True,
                     download_name=file["original_filename"]
                    )

@routes.route("/delete/<stored_filename>", methods=["POST"])
def delete(stored_filename):

    file = database.get_file(stored_filename)
    if file is None:
            abort(404)

    
    destination = config.UPLOAD_FOLDER / file["stored_filename"]
    if not destination.is_file():
            abort(404)

    try:
        destination.unlink()
        database.delete_file(stored_filename)
    except Exception:
            abort(500)

    
    return render_template("deleted.html", f = file["original_filename"])
