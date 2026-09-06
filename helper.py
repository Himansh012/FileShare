import database

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
        prefix = original_filename.split(".")[0]
        suffix = original_filename.split(".")[1]
        original_filename = f"{prefix}({file_count}).{suffix}"
    return original_filename