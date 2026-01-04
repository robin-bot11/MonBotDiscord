# db_postgres.py
import asyncpg
import os
import asyncio
from datetime import datetime

# ================= CONFIG =================
SNIPE_EXPIRATION = int(os.getenv("SNIPE_EXPIRATION", 86400))  # 24h par défaut
CLEANUP_INTERVAL = 3600  # 1h

# ================= DATABASE =================
class DatabasePG:
    """Gestion PostgreSQL complète pour le bot Discord."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self._cleanup_task = None

    # ---------- FACTORY ----------
    @classmethod
    async def create(cls, database_url: str):
        """Initialise la base PostgreSQL + tables."""
        pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=1,
            max_size=5,
            command_timeout=60
        )

        self = cls(pool)

        async with pool.acquire() as conn:
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id SERIAL PRIMARY KEY,
                guild_id BIGINT,
                member_id BIGINT,
                reason TEXT,
                staff BIGINT,
                date TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS mutes (
                id SERIAL PRIMARY KEY,
                guild_id BIGINT,
                member_id BIGINT,
                reason TEXT,
                staff BIGINT,
                date TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS logs (
                guild_id BIGINT,
                log_type TEXT,
                channel_id BIGINT,
                PRIMARY KEY (guild_id, log_type)
            );

            CREATE TABLE IF NOT EXISTS welcome (
                guild_id BIGINT PRIMARY KEY,
                channel_id BIGINT,
                message TEXT,
                embed JSONB,
                enabled BOOLEAN DEFAULT TRUE
            );

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

            CREATE TABLE IF NOT EXISTS partner (
                guild_id BIGINT PRIMARY KEY,
                role_id BIGINT,
                channel_id BIGINT
            );

            CREATE TABLE IF NOT EXISTS snipes (
                channel_id BIGINT PRIMARY KEY,
                author BIGINT,
                content TEXT,
                timestamp BIGINT
            );
            """)

        # Lance le cleanup automatique
        self._cleanup_task = asyncio.create_task(self._cleanup_snipes_loop())

        return self

    # ================= CLEANUP =================
    async def _cleanup_snipes_loop(self):
        """Supprime automatiquement les snipes expirés."""
        while True:
            try:
                async with self.pool.acquire() as conn:
                    limit = int(datetime.utcnow().timestamp()) - SNIPE_EXPIRATION
                    await conn.execute(
                        "DELETE FROM snipes WHERE timestamp < $1;",
                        limit
                    )
            except Exception as e:
                print(f"[DB] Cleanup snipes error: {e}")

            await asyncio.sleep(CLEANUP_INTERVAL)

    async def close(self):
        if self._cleanup_task:
            self._cleanup_task.cancel()
        await self.pool.close()

    # ================= LOGS =================
    async def set_log_channel(self, guild_id, log_type, channel_id):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO logs (guild_id, log_type, channel_id)
            VALUES ($1,$2,$3)
            ON CONFLICT (guild_id, log_type)
            DO UPDATE SET channel_id=$3;
            """, guild_id, log_type, channel_id)

    async def get_log_channel(self, guild_id, log_type):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT channel_id FROM logs WHERE guild_id=$1 AND log_type=$2;",
                guild_id, log_type
            )

    # ================= WARNS =================
    async def add_warn(self, guild_id, member_id, reason, staff):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO warns (guild_id, member_id, reason, staff, date)
            VALUES ($1,$2,$3,$4,$5);
            """, guild_id, member_id, reason, staff, datetime.utcnow())

    async def get_warns(self, guild_id, member_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
            SELECT * FROM warns
            WHERE guild_id=$1 AND member_id=$2
            ORDER BY date;
            """, guild_id, member_id)

    async def del_warn(self, warn_id):
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM warns WHERE id=$1;",
                warn_id
            )
            return result.endswith("1")

    # ================= MUTES =================
    async def add_mute(self, guild_id, member_id, reason, staff):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO mutes (guild_id, member_id, reason, staff, date)
            VALUES ($1,$2,$3,$4,$5);
            """, guild_id, member_id, reason, staff, datetime.utcnow())

    async def get_mutes(self, guild_id, member_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
            SELECT * FROM mutes
            WHERE guild_id=$1 AND member_id=$2
            ORDER BY date;
            """, guild_id, member_id)

    async def remove_mute(self, guild_id, member_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM mutes WHERE guild_id=$1 AND member_id=$2;",
                guild_id, member_id
            )

    # ================= WELCOME =================
    async def set_welcome(self, guild_id, channel_id, message, embed, enabled=True):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO welcome (guild_id, channel_id, message, embed, enabled)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (guild_id)
            DO UPDATE SET channel_id=$2, message=$3, embed=$4, enabled=$5;
            """, guild_id, channel_id, message, embed, enabled)

    async def get_welcome(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM welcome WHERE guild_id=$1;",
                guild_id
            )

    # ================= VERIFICATION =================
    async def get_verification(self, guild_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM verification WHERE guild_id=$1;",
                guild_id
            )
            return dict(row) if row else None

    async def add_try(self, guild_id, member_id):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            UPDATE verification
            SET tries = jsonb_set(
                tries,
                ARRAY[$2]::text[],
                to_jsonb(COALESCE((tries->>$2)::int, 0) + 1)
            )
            WHERE guild_id=$1;
            """, guild_id, str(member_id))

    # ================= PARTNER =================
    async def set_partner(self, guild_id, role_id=None, channel_id=None):
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO partner (guild_id, role_id, channel_id)
            VALUES ($1,$2,$3)
            ON CONFLICT (guild_id)
            DO UPDATE SET role_id=$2, channel_id=$3;
            """, guild_id, role_id, channel_id)

    async def get_partner(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM partner WHERE guild_id=$1;",
                guild_id
            )

    # ================= SNIPES =================
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
                "SELECT * FROM snipes WHERE channel_id=$1;",
                channel_id
            )
            if not row:
                return None

            if int(datetime.utcnow().timestamp()) - row["timestamp"] > SNIPE_EXPIRATION:
                await conn.execute(
                    "DELETE FROM snipes WHERE channel_id=$1;",
                    channel_id
                )
                return None

            return row
