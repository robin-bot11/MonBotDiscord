# db_postgres.py
import asyncpg
import os
from datetime import datetime

SNIPE_EXPIRATION = int(os.getenv("SNIPE_EXPIRATION", 86400))


class DatabasePG:
    """Gestion PostgreSQL pour le bot Discord"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @staticmethod
    async def create(database_url: str):
        """
        Initialise PostgreSQL et retourne une instance DatabasePG
        """
        pool = await asyncpg.create_pool(database_url)
        db = DatabasePG(pool)

        async with pool.acquire() as conn:
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                guild_id BIGINT,
                member_id BIGINT,
                reason TEXT,
                staff BIGINT,
                date TIMESTAMP
            );
            """)

            await conn.execute("""
            CREATE TABLE IF NOT EXISTS mutes (
                guild_id BIGINT,
                member_id BIGINT,
                reason TEXT,
                staff BIGINT,
                date TIMESTAMP
            );
            """)

            await conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                guild_id BIGINT,
                log_type TEXT,
                channel_id BIGINT,
                PRIMARY KEY (guild_id, log_type)
            );
            """)

            await conn.execute("""
            CREATE TABLE IF NOT EXISTS welcome (
                guild_id BIGINT PRIMARY KEY,
                channel_id BIGINT,
                message TEXT,
                embed JSONB,
                enabled BOOLEAN DEFAULT TRUE
            );
            """)

            await conn.execute("""
            CREATE TABLE IF NOT EXISTS verification (
                guild_id BIGINT PRIMARY KEY,
                role_valid BIGINT,
                isolation_role BIGINT,
                title TEXT,
                description TEXT,
                button_text TEXT,
                message_id BIGINT,
                emoji TEXT,
                tries JSONB DEFAULT '{}'::jsonb
            );
            """)

            await conn.execute("""
            CREATE TABLE IF NOT EXISTS partner (
                guild_id BIGINT PRIMARY KEY,
                role_id BIGINT,
                channel_id BIGINT
            );
            """)

            await conn.execute("""
            CREATE TABLE IF NOT EXISTS snipes (
                channel_id BIGINT PRIMARY KEY,
                author BIGINT,
                content TEXT,
                timestamp BIGINT
            );
            """)

        return db

    # ---------- SNIPES ----------
    async def set_snipe(self, channel_id, author_id, content):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO snipes (channel_id, author, content, timestamp)
            VALUES ($1,$2,$3,$4)
            ON CONFLICT (channel_id)
            DO UPDATE SET author=$2, content=$3, timestamp=$4;
            """, channel_id, author_id, content, int(datetime.utcnow().timestamp()))

    async def get_snipe(self, channel_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM snipes WHERE channel_id=$1;", channel_id
            )
            if not row:
                return None

            if int(datetime.utcnow().timestamp()) - row["timestamp"] > SNIPE_EXPIRATION:
                await conn.execute(
                    "DELETE FROM snipes WHERE channel_id=$1;", channel_id
                )
                return None

            return row
