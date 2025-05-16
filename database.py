import sqlite3


def get_connection():
    return sqlite3.connect('HabitTrack.db')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT,
            first_name TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            dispatch_date TEXT,
            is_completed BOOLEAN,
            FOREIGN KEY(habit_id) REFERENCES Habits(id)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()