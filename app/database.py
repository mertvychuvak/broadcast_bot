import aiosqlite
from datetime import datetime

DB_NAME = "bot.db"

# 👇 твой стартовый админ
INITIAL_ADMIN_ID = 53225555


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        # --- GROUPS ---
        await db.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            title TEXT,
            members_count INTEGER
        )
        """)

        # --- ADMINS ---
        await db.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
        """)

        # --- BROADCASTS ---
        await db.execute("""
        CREATE TABLE IF NOT EXISTS broadcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            created_at TEXT
        )
        """)

        # --- SENT MESSAGES ---
        await db.execute("""
        CREATE TABLE IF NOT EXISTS sent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broadcast_id INTEGER,
            group_id INTEGER,
            message_id INTEGER
        )
        """)

        # 👇 гарантированно добавляем стартового админа
        await db.execute(
            "INSERT OR IGNORE INTO admins (user_id) VALUES (?)",
            (INITIAL_ADMIN_ID,)
        )

        await db.commit()


# ----------------- ADMINS -----------------

async def add_admin(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO admins (user_id) VALUES (?)",
            (user_id,)
        )
        await db.commit()


async def get_admins():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM admins") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]


# ----------------- GROUPS -----------------

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


# ----------------- BROADCASTS -----------------

async def add_broadcast(text):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        INSERT INTO broadcasts (text, created_at)
        VALUES (?, ?)
        """, (text, datetime.utcnow().isoformat()))
        await db.commit()
        return cur.lastrowid


async def get_broadcasts():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
        SELECT id, text FROM broadcasts
        ORDER BY id DESC
        """) as cursor:
            return await cursor.fetchall()


async def get_sent_messages(broadcast_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
        SELECT group_id, message_id
        FROM sent_messages
        WHERE broadcast_id=?
        """, (broadcast_id,)) as cursor:
            return await cursor.fetchall()


async def add_sent_message(broadcast_id, group_id, message_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO sent_messages (broadcast_id, group_id, message_id)
        VALUES (?, ?, ?)
        """, (broadcast_id, group_id, message_id))
        await db.commit()
