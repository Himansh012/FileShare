"""
Database helper functions for the FileShare application.

Handles SQLite connection management and CRUD operations
for uploaded file metadata.
"""

import sqlite3
from flask import g
import config

DATABASE = config.DATABASE

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
            upload_time TEXT,
            size INTEGER NOT NULL,
            recovered INTEGER NOT NULL DEFAULT 0 
            CHECK (recovered IN (0,1))
        )
    """)

    db.commit()

def close_db(exception=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def create_file(file_uuid, original_filename, stored_filename, upload_time, size, recovered=0):

    db = get_db()
    db.execute("""
        INSERT INTO files(
                file_uuid,
                original_filename,
                stored_filename,
                upload_time,
                size,
                recovered
            ) 
            VALUES(
                ?, ?, ?, ?, ?, ?
            )
    """, (
        file_uuid,
        original_filename,
        stored_filename,
        upload_time,
        size,
        recovered
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
