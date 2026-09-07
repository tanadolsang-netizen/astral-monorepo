"""
Event mapping service — เชื่อมโยง transit กับเหตุการณ์ชีวิตจริง
"""
import sqlite3
import logging
import uuid
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("astral.events")

DB_PATH = Path(__file__).resolve().parents[2] / "astral.db"

class EventService:
    def __init__(self):
        self.db_path = DB_PATH
    
    def record_event(self, user_id: str, event_date: str, category: str, 
                     description: str, significance: int = 3, related_transit: str = "") -> dict:
        """บันทึกเหตุการณ์ชีวิต"""
        event_id = str(uuid.uuid4())[:12]
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("""
            INSERT INTO life_events (id, user_id, event_date, category, description, significance, related_transit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event_id, user_id, event_date, category, description, significance, related_transit))
        con.commit()
        con.close()
        return {"status": "ok", "event_id": event_id}
    
    def get_events(self, user_id: str, category: str = "") -> list:
        """ดูเหตุการณ์ทั้งหมด"""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        if category:
            cur.execute("SELECT * FROM life_events WHERE user_id = ? AND category = ? ORDER BY event_date DESC", (user_id, category))
        else:
            cur.execute("SELECT * FROM life_events WHERE user_id = ? ORDER BY event_date DESC", (user_id,))
        results = [{"id": r[0], "user_id": r[1], "date": r[2], "category": r[3], 
                    "description": r[4], "significance": r[5], "transit": r[6]} for r in cur.fetchall()]
        con.close()
        return results
    
    def find_transit_event_correlations(self, user_id: str) -> list:
        """หาความสัมพันธ์ระหว่าง transit กับเหตุการณ์"""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("""
            SELECT le.category, le.description, le.related_transit, le.significance
            FROM life_events le
            WHERE le.user_id = ? AND le.related_transit != ''
            ORDER BY le.significance DESC
        """, (user_id,))
        results = [{"category": r[0], "description": r[1], "transit": r[2], "significance": r[3]} for r in cur.fetchall()]
        con.close()
        return results

event_service = EventService()
