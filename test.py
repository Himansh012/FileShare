import sqlite3


connection = sqlite3.connect('fileshare.db')

cursor = connection.cursor()

print(cursor.fetchall())