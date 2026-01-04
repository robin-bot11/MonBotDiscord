# database_pg.py
import asyncpg
from datetime import datetime

SNIPE_EXPIRATION = 86400  # 24 heures

# Remplace directement par ton lien PostgreSQL fourni par Railway
DATABASE_URL = "postgres://user:password@host:port/database"

class DatabasePG:
    """Gestion complète de la DB PostgreSQL pour le bot Discord."""

    def __init__(self, pool):
        self.pool = pool

    @classmethod
    async def create(cls):
        """Initialise le pool PostgreSQL et crée les tables si nécessaire."""
        self = cls(await asyncpg.create_pool(DATABASE_URL))
        async with self.pool.acquire() as conn:
            # Tables principales
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
            CREATE TABLE IF NOT EXISTS snipes (
                channel_id BIGINT PRIMARY KEY,
                author BIGINT,
                content TEXT,
                timestamp BIGINT
            );
            """)
        return self

    # ------------------ LOG CHANNEL ------------------
    async def set_log_channel(self, guild_id, log_type, channel_id):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO logs (guild_id, log_type, channel_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (guild_id, log_type) DO UPDATE SET channel_id = $3;
            """, guild_id, log_type, channel_id)

    async def get_log_channel(self, guild_id, log_type):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
            SELECT channel_id FROM logs WHERE guild_id = $1 AND log_type = $2;
            """, guild_id, log_type)
            return row["channel_id"] if row else None

    # ------------------ WARNS ------------------
    async def add_warn(self, guild_id, member_id, reason, staff):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO warns (guild_id, member_id, reason, staff, date)
            VALUES ($1, $2, $3, $4, $5);
            """, guild_id, member_id, reason, staff, datetime.utcnow())

    async def get_warns(self, guild_id, member_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
            SELECT * FROM warns WHERE guild_id = $1 AND member_id = $2 ORDER BY date;
            """, guild_id, member_id)

    async def del_warn(self, guild_id, member_id, warn_id):
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
            DELETE FROM warns
            WHERE ctid = (SELECT ctid FROM warns WHERE guild_id = $1 AND member_id = $2 ORDER BY date OFFSET $3 LIMIT 1);
            """, guild_id, member_id, warn_id)
            return result.endswith("1")

    # ------------------ MUTES ------------------
    async def add_mute(self, guild_id, member_id, reason, staff):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO mutes (guild_id, member_id, reason, staff, date)
            VALUES ($1, $2, $3, $4, $5);
            """, guild_id, member_id, reason, staff, datetime.utcnow())

    async def get_mutes(self, guild_id, member_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
            SELECT * FROM mutes WHERE guild_id = $1 AND member_id = $2 ORDER BY date;
            """, guild_id, member_id)

    async def remove_mute(self, guild_id, member_id):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            DELETE FROM mutes WHERE guild_id = $1 AND member_id = $2;
            """, guild_id, member_id)

    # ------------------ WELCOME ------------------
    async def set_welcome(self, guild_id, channel_id=None, message=None, embed_data=None, enabled=True):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO welcome (guild_id, channel_id, message, embed, enabled)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id) DO UPDATE SET
            channel_id = $2, message = $3, embed = $4, enabled = $5;
            """, guild_id, channel_id, message, embed_data, enabled)

    async def get_welcome(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
            SELECT * FROM welcome WHERE guild_id = $1;
            """, guild_id)

    # ------------------ SNIPES ------------------
    async def set_snipe(self, channel_id, author_id, content):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO snipes (channel_id, author, content, timestamp)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (channel_id) DO UPDATE SET
            author = $2, content = $3, timestamp = $4;
            """, channel_id, author_id, content, int(datetime.utcnow().timestamp()))

    async def get_snipe(self, channel_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
            SELECT * FROM snipes WHERE channel_id = $1;
            """, channel_id)
            if not row:
                return None
            if int(datetime.utcnow().timestamp()) - row["timestamp"] > SNIPE_EXPIRATION:
                await conn.execute("DELETE FROM snipes WHERE channel_id = $1;", channel_id)
                return None
            return row

    async def clear_guild_snipes(self, guild):
        async with self.pool.acquire() as conn:
            channels = [c.id for c in guild.text_channels]
            await conn.execute("""
            DELETE FROM snipes WHERE channel_id = ANY($1::bigint[]);
            """, channels)
