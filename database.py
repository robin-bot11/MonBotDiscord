# database.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect("botdata.db")
cursor = conn.cursor()

# --- Bienvenue ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS welcome_config (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    message TEXT
)
""")

# --- Warns ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS warns (
    guild_id INTEGER,
    user_id INTEGER,
    reason TEXT,
    author_id INTEGER,
    date TEXT
)
""")

# --- Lock roles ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS locked_roles (
    guild_id INTEGER,
    role_id INTEGER
)
""")

# --- Giveaways ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS giveaways (
    guild_id INTEGER,
    message_id INTEGER,
    reward TEXT,
    end_time TEXT,
    author_id INTEGER
)
""")

# --- Règles ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS rules (
    guild_id INTEGER PRIMARY KEY,
    title TEXT,
    text TEXT,
    role_id INTEGER,
    button_text TEXT,
    button_emoji TEXT
)
""")

conn.commit()

def add_warn(guild_id, user_id, reason, author_id):
    date = datetime.utcnow().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO warns VALUES (?, ?, ?, ?, ?)",
                   (guild_id, user_id, reason, author_id, date))
    conn.commit()

def get_warns(guild_id, user_id):
    cursor.execute("SELECT rowid, reason, author_id, date FROM warns WHERE guild_id=? AND user_id=?",
                   (guild_id, user_id))
    return cursor.fetchall()

def remove_warn(guild_id, rowid):
    cursor.execute("DELETE FROM warns WHERE rowid=? AND guild_id=?",
                   (rowid, guild_id))
    conn.commit()
