import aiosqlite
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# DB_PATH = Path.home() / ".local" / "share" / "taque" / "taque.db"
DB_PATH = Path.cwd() / "taque.db"

def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            event_type TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

async def log_event(event_type: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now(timezone.utc).timestamp()
        await db.execute(
            "INSERT INTO events (timestamp, event_type) VALUES (?, ?)",
            (now, event_type)
        )
        await db.commit()

async def get_current_state() -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 1") as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

async def get_today_total_seconds():
    async with aiosqlite.connect(DB_PATH) as db:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).timestamp()
        
        async with db.execute(
            "SELECT timestamp, event_type FROM events WHERE timestamp >= ? ORDER BY timestamp ASC", 
            (start_of_day,)
        ) as cursor:
            events = await cursor.fetchall()
            
            # Encontrar o último STOP (se existir)
            last_stop_index = None
            for i, (timestamp, event_type) in enumerate(events):
                if event_type == "STOP":
                    last_stop_index = i
            
            # Se houve STOP, ignorar tudo antes dele
            if last_stop_index is not None:
                events = events[last_stop_index + 1:]
            
            total_seconds = 0
            work_start = None
            
            for timestamp, event_type in events:
                if event_type == "START_WORK":
                    if work_start is None:
                        work_start = timestamp
                else: # START_BREAK (STOP já foi filtrado)
                    if work_start is not None:
                        total_seconds += (timestamp - work_start)
                        work_start = None
            
            return total_seconds