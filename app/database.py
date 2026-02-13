import aiosqlite
from datetime import datetime

DB_NAME = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            title TEXT,
            members_count INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS broadcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            created_at TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS sent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broadcast_id INTEGER,
            group_id INTEGER,
            message_id INTEGER
        )
        """)

        await db.commit()


async def add_group(group_id, title, members_count):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR REPLACE INTO groups (id, title, members_count)
        VALUES (?, ?, ?)
        """, (group_id, title, members_count))
        await db.commit()


async def get_groups():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM groups") as cursor:
            return await cursor.fetchall()


async def add_broadcast(text):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        INSERT INTO broadcasts (text, created_at)
        VALUES (?, ?)
        """, (text, datetime.utcnow().isoformat()))
        await db.commit()
        return cur.lastrowid


async def add_sent_message(broadcast_id, group_id, message_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO sent_messages (broadcast_id, group_id, message_id)
        VALUES (?, ?, ?)
        """, (broadcast_id, group_id, message_id))
        await db.commit()
