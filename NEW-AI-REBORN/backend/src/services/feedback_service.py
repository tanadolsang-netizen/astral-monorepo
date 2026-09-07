"""
Feedback service — เก็บ feedback จาก user + ปรับปรุง narrative
"""
import sqlite3
import logging
import uuid
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("astral.feedback")

DB_PATH = Path(__file__).resolve().parents[2] / "astral.db"

class FeedbackService:
    def __init__(self):
        self.db_path = DB_PATH
    
    def submit_feedback(self, reading_id: str, user_id: str, rating: int, 
                        comment: str = "", section: str = "") -> dict:
        """บันทึก feedback"""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("""
            INSERT INTO user_feedback (reading_id, user_id, rating, comment, section)
            VALUES (?, ?, ?, ?, ?)
        """, (reading_id, user_id, rating, comment, section))
        con.commit()
        con.close()
        return {"status": "ok", "reading_id": reading_id, "rating": rating}
    
    def get_feedback_stats(self, user_id: str = "") -> dict:
        """ดูสถิติ feedback"""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        if user_id:
            cur.execute("SELECT AVG(rating), COUNT(*) FROM user_feedback WHERE user_id = ?", (user_id,))
        else:
            cur.execute("SELECT AVG(rating), COUNT(*) FROM user_feedback")
        avg, count = cur.fetchone()
        con.close()
        return {"average_rating": round(avg or 0, 2), "total_feedback": count or 0}
    
    def get_low_rated_sections(self) -> list:
        """ดู sections ที่ได้ rating ต่ำ — ต้องปรับปรุง"""
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("""
            SELECT section, AVG(rating) as avg_rating, COUNT(*) as count
            FROM user_feedback
            WHERE section != ''
            GROUP BY section
            HAVING avg_rating < 3
            ORDER BY avg_rating ASC
        """)
        results = [{"section": r[0], "avg_rating": round(r[1], 2), "count": r[2]} for r in cur.fetchall()]
        con.close()
        return results

feedback_service = FeedbackService()
