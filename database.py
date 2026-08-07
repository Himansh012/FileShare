"""
Database helper functions for the FileShare application.

Handles SQLite connection management and CRUD operations
for uploaded file metadata.
"""

import sqlite3
from flask import g

DATABASE = "fileshare.db"

def get_db():

    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db 

def init_db():

    db = get_db()

    db.execute("""
            CREATE TABLE IF NOT EXISTS files(
            id INTEGER PRIMARY KEY,
            file_uuid TEXT UNIQUE NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT UNIQUE NOT NULL,
            upload_time TEXT NOT NULL,
            size INTEGER NOT NULL
        )
    """)

    db.commit()

def close_db(exception=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def create_file(file_uuid, original_filename, stored_filename, upload_time, size):

    db = get_db()
    db.execute("""
        INSERT INTO files(
                file_uuid,
                original_filename,
                stored_filename,
                upload_time,
                size
            ) 
            VALUES(
                ?, ?, ?, ?, ?
            )
    """, (
        file_uuid,
        original_filename,
        stored_filename,
        upload_time,
        size
    ))

    db.commit()

def list_files():

    db = get_db()
    return db.execute("""
    SELECT * 
    FROM files 
    ORDER by upload_time DESC;
    """).fetchall()
     

def get_file(stored_filename):

    db = get_db()
    return db.execute("""
    SELECT * 
    FROM files
    WHERE stored_filename=?;""",
    (stored_filename,)
    ).fetchone()


def delete_file(stored_filename):

    db = get_db()
    db.execute("DELETE FROM files WHERE stored_filename = ?", (stored_filename,))

    db.commit()