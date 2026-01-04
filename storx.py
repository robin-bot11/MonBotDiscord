import asyncpg
import os
import logging
from datetime import datetime, timezone

log = logging.getLogger(__name__)


class DatabasePG:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    # =========================
    # INIT / CONNEXION
    # =========================
    @classmethod
    async def create(cls):
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError("❌ DATABASE_URL manquant dans l'environnement")

        log.info("🔄 Connexion à PostgreSQL...")

        pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=1,
            max_size=5,
            command_timeout=60,
        )

        self = cls(pool)
        await self._init_tables()

        log.info("✅ PostgreSQL prêt")
        return self

    async def close(self):
        await self.pool.close()

    # =========================
    # TABLES
    # =========================
    async def _init_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS snipes (
                    id SERIAL PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    author_id BIGINT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMPTZ NOT NULL
                );
            """)

    # =========================
    # SNIPE
    # =========================
    async def add_snipe(self, guild_id, channel_id, author_id, content):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO snipes (guild_id, channel_id, author_id, content, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """,
            guild_id,
            channel_id,
            author_id,
            content,
            datetime.now(timezone.utc)
            )

    async def get_last_snipe(self, guild_id, channel_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT author_id, content, created_at
                FROM snipes
                WHERE guild_id = $1 AND channel_id = $2
                ORDER BY created_at DESC
                LIMIT 1
            """, guild_id, channel_id)

    # =========================
    # CLEANUP AUTOMATIQUE
    # =========================
    async def cleanup_snipes(self):
        expiration = int(os.getenv("SNIPE_EXPIRATION", 86400))
        async with self.pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM snipes
                WHERE created_at < NOW() - ($1 || ' seconds')::interval
            """, expiration)

    # =========================
    # UTILS
    # =========================
    async def ping(self) -> bool:
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False
