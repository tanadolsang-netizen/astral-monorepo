
"""
Database migration for 99% accuracy — feedback loop + event mapping.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "astral.db"

def migrate():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    # ========================================
    # 1. NARRATIVE READINGS — บันทึกทุกครั้งที่สร้าง narrative
    # ========================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS narrative_readings (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            chart_id TEXT NOT NULL,
            reading_type TEXT NOT NULL,
            narrative_json TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # ========================================
    # 2. USER FEEDBACK — ประเมินความถูกต้อง
    # ========================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reading_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            section TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # ========================================
    # 3. LIFE EVENTS — บันทึกเหตุการณ์ชีวิตจริง
    # ========================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS life_events (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            event_date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            significance INTEGER DEFAULT 3,
            related_transit TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # ========================================
    # 4. TRANSIT TRACKING — ติดตาม transit ที่กระตุ้น
    # ========================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transit_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            transit_planet TEXT NOT NULL,
            natal_planet TEXT NOT NULL,
            aspect TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            intensity REAL DEFAULT 1.0,
            event_id TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # ========================================
    # 5. USER PREFERENCES — ตั้งค่าส่วนตัว
    # ========================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            preferred_system TEXT DEFAULT 'tropical',
            preferred_house_system TEXT DEFAULT 'placidus',
            narrative_depth TEXT DEFAULT 'detailed',
            language TEXT DEFAULT 'th',
            notifications_enabled INTEGER DEFAULT 1,
            notification_time TEXT DEFAULT '07:00',
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    con.commit()
    print("Migration complete — 5 new tables created")
    
    # Verify tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Tables: {tables}")
    
    con.close()

if __name__ == "__main__":
    migrate()
