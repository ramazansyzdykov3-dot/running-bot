import aiosqlite
from datetime import date
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id   INTEGER PRIMARY KEY,
                username  TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS runs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                date            DATE    NOT NULL,
                distance_km     REAL    NOT NULL,
                duration_min    REAL    NOT NULL,
                pace_sec_per_km INTEGER NOT NULL,
                notes           TEXT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS monthly_goals (
                user_id  INTEGER NOT NULL,
                year     INTEGER NOT NULL,
                month    INTEGER NOT NULL,
                goal_km  REAL    NOT NULL,
                PRIMARY KEY (user_id, year, month),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        await db.commit()


async def ensure_user(user_id: int, username: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
        )
        await db.commit()


async def add_run(
    user_id: int,
    distance_km: float,
    duration_min: float,
    pace_sec_per_km: int,
    notes: str | None,
    run_date: date,
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO runs (user_id, date, distance_km, duration_min, pace_sec_per_km, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, run_date.isoformat(), distance_km, duration_min, pace_sec_per_km, notes),
        )
        await db.commit()


async def get_runs(user_id: int, limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM runs WHERE user_id=? ORDER BY date DESC, created_at DESC LIMIT ?",
            (user_id, limit),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_runs_for_period(user_id: int, year: int, month: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM runs
               WHERE user_id=? AND strftime('%Y', date)=? AND strftime('%m', date)=?
               ORDER BY date""",
            (user_id, str(year), f"{month:02d}"),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_runs_last_n_days(user_id: int, days: int = 30) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM runs
               WHERE user_id=? AND date >= date('now', ?)
               ORDER BY date""",
            (user_id, f"-{days} days"),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_total_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT
                COUNT(*)            AS total_runs,
                COALESCE(SUM(distance_km), 0)  AS total_km,
                COALESCE(MIN(pace_sec_per_km), 0) AS best_pace,
                COALESCE(AVG(pace_sec_per_km), 0) AS avg_pace
               FROM runs WHERE user_id=?""",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
    return {
        "total_runs": row[0],
        "total_km": row[1],
        "best_pace": row[2],
        "avg_pace": row[3],
    }


async def set_monthly_goal(user_id: int, year: int, month: int, goal_km: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO monthly_goals (user_id, year, month, goal_km)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, year, month) DO UPDATE SET goal_km=excluded.goal_km""",
            (user_id, year, month, goal_km),
        )
        await db.commit()


async def get_monthly_goal(user_id: int, year: int, month: int) -> float | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT goal_km FROM monthly_goals WHERE user_id=? AND year=? AND month=?",
            (user_id, year, month),
        ) as cur:
            row = await cur.fetchone()
    return row[0] if row else None


def calc_pace(distance_km: float, duration_min: float) -> tuple[int, int]:
    pace_sec = (duration_min * 60) / distance_km
    return int(pace_sec // 60), int(pace_sec % 60)


def format_pace(minutes: int, seconds: int) -> str:
    return f"{minutes}:{seconds:02d} мин/км"


def parse_duration(text: str) -> float | None:
    """Парсит '30:15' или '30' → минуты (float). Возвращает None при ошибке."""
    text = text.strip().replace(",", ".")
    if ":" in text:
        parts = text.split(":")
        if len(parts) != 2:
            return None
        try:
            m, s = int(parts[0]), int(parts[1])
            if s < 0 or s >= 60:
                return None
            return m + s / 60
        except ValueError:
            return None
    else:
        try:
            return float(text)
        except ValueError:
            return None
