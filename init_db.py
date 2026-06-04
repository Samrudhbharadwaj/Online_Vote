import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
password TEXT,
voted INTEGER DEFAULT 0
)
""")

conn.execute("""
CREATE TABLE candidates (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
votes INTEGER DEFAULT 0
)
""")

conn.execute("""
CREATE TABLE election (
id INTEGER PRIMARY KEY,
status TEXT
)
""")

conn.execute("INSERT INTO election (id, status) VALUES (1, 'stopped')")

conn.commit()
conn.close()

print("Database created successfully!")