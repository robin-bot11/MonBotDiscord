import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("bot.db")
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        # Bienvenue
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS welcome (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message TEXT
        )
        """)

        # Snipe
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS snipe (
            channel_id INTEGER PRIMARY KEY,
            author TEXT,
            content TEXT
        )
        """)

        self.conn.commit()

    # ---------- BIENVENUE ----------
    def set_welcome(self, guild_id, channel_id, message):
        self.cursor.execute(
            "INSERT OR REPLACE INTO welcome VALUES (?, ?, ?)",
            (guild_id, channel_id, message)
        )
        self.conn.commit()

    def get_welcome(self, guild_id):
        self.cursor.execute(
            "SELECT channel_id, message FROM welcome WHERE guild_id = ?",
            (guild_id,)
        )
        return self.cursor.fetchone()

    # ---------- SNIPE ----------
    def set_snipe(self, channel_id, author, content):
        self.cursor.execute(
            "INSERT OR REPLACE INTO snipe VALUES (?, ?, ?)",
            (channel_id, author, content)
        )
        self.conn.commit()

    def get_snipe(self, channel_id):
        self.cursor.execute(
            "SELECT author, content FROM snipe WHERE channel_id = ?",
            (channel_id,)
        )
        return self.cursor.fetchone()

db = Database()
