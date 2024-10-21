# database.py
import sqlite3
from datetime import datetime

DATABASE = 'agentbot.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            nome_evento TEXT NOT NULL,
            data_evento TEXT,
            hora_evento TEXT,
            local TEXT,
            descricao TEXT,
            status TEXT,
            confirmados TEXT DEFAULT '[]',
            chat TEXT,
            datetime TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config_gpt (
            id INTEGER PRIMARY KEY,
            system_prompt TEXT, 
            chat TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            chat TEXT,
            sender TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database when module is imported
init_db()
