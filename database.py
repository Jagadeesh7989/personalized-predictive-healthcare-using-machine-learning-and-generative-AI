import sqlite3

def create_tables():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ✅ USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # ✅ PREDICTIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        fever INTEGER,
        cough INTEGER,
        headache INTEGER,
        fatigue INTEGER,
        rashes INTEGER,
        chest INTEGER,
        risk TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()