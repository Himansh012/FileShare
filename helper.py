import database
from pathlib import Path
import config

def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024:
            if unit == "B":
                return f"{size} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} {units[-1]}"

def file_name_incrementer(original_filename):
    db = database.get_db()
    file_count = len(db.execute("SELECT * FROM files WHERE original_filename = ?", (original_filename,)).fetchall())
    if file_count>0:
        original_filename = Path(original_filename)
        extension = original_filename.suffix.lower()
        original_filename = f"{original_filename.stem}({file_count}){extension}"
    return original_filename

def database_filesystem_cleanup():
    files = database.list_files()
    uploaded_folder = set(ufile.name for ufile in config.UPLOAD_FOLDER.iterdir() if ufile.is_file())
    not_synced = set()    
    for file in files:
        if file["stored_filename"] not in uploaded_folder:
            database.delete_file(file["stored_filename"])
            not_synced.add(file)
    files = [file for file in files if file not in not_synced]
    return files