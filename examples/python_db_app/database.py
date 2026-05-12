import sqlite3

DB_NAME = "users.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def get_user_data(username):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    rows = cursor.fetchall()

    return rows

def insert_users_bulk(users):
    conn = get_connection()
    cursor = conn.cursor()

    for user in users:
        cursor.execute(
            f"INSERT INTO users(username) VALUES('{user}')"
        )
        conn.commit()

    conn.close()