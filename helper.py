import database
from pathlib import Path
import config
import uuid

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



def database_filesystem_synchronization():

## Synchronizes the files that are visible in filesystem but not in database

    files_in_system = config.UPLOAD_FOLDER.iterdir()
    database_files = database.list_files()
    filesystem_files = []
    for i in database_files:
        filesystem_files.append(i['stored_filename'])

    for i in files_in_system:
        if not i.is_file():
            continue
        if i.name not in filesystem_files:
            parts = i.name.split("_",1)
            if(len(parts)<=1):
                continue
            file_uuid = parts[0]
            try:
                uuid.UUID(file_uuid) ## valid UUID check, if not a valid UUID it returns ValueError
            except ValueError:
                continue
            if database.file_uuid_exists(file_uuid):
                i.unlink()
                continue

            original_filename = parts[1]
            stored_filename = i.name
            file_stats = i.stat()
            upload_time = None
            size = file_stats.st_size   
            database.create_file(file_uuid, original_filename, stored_filename, upload_time, size, recovered=1)

    ## Synchronizes the files that are visible in database but not in filesystem

    database_files = database.list_files()
    uploaded_files = set(ufile.name for ufile in config.UPLOAD_FOLDER.iterdir() if ufile.is_file())
    not_synced = set()    
    for file in database_files:
        if file["stored_filename"] not in uploaded_files:
            database.delete_file(file["stored_filename"])
            not_synced.add(file)
    database_files = [file for file in database_files if file not in not_synced]
            
    return database_files