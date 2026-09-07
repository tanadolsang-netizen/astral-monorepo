"""
User preference service — ตั้งค่าส่วนตัว
"""
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger("astral.user_pref")

DB_PATH = Path(__file__).resolve().parents[2] / "astral.db"

class UserPreferenceService:
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_preferences(self, user_id: str) -> dict:
        """ดู preferences"""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        con.close()
        if row:
            return {
                "user_id": row[0],
                "preferred_system": row[1],
                "preferred_house_system": row[2],
                "narrative_depth": row[3],
                "language": row[4],
                "notifications_enabled": bool(row[5]),
                "notification_time": row[6],
            }
        return {}
    
    def set_preferences(self, user_id: str, **kwargs) -> dict:
        """ตั้งค่า preferences"""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO user_preferences (user_id, preferred_system, preferred_house_system, narrative_depth, language, notifications_enabled, notification_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            kwargs.get("preferred_system", "tropical"),
            kwargs.get("preferred_house_system", "placidus"),
            kwargs.get("narrative_depth", "detailed"),
            kwargs.get("language", "th"),
            kwargs.get("notifications_enabled", 1),
            kwargs.get("notification_time", "07:00"),
        ))
        con.commit()
        con.close()
        return {"status": "ok", "user_id": user_id}

user_pref_service = UserPreferenceService()
