import sqlite3
from datetime import datetime
import os
from config import DATABASE_FILE


class CandidateDatabase:
    """Manages all database operations for candidates"""

    def __init__(self):
        self.db_file = DATABASE_FILE
        self.create_tables()
        self.ensure_schema_updates()

    # =========================
    # TABLE CREATION
    # =========================
    def create_tables(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Candidates table (BASE STRUCTURE)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                resume_file TEXT,
                match_score REAL,
                summary TEXT,
                status TEXT,
                created_at TEXT,
                application_date TEXT
            )
        ''')

        # Email logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                email_type TEXT,
                subject TEXT,
                status TEXT,
                sent_at TEXT
            )
        ''')

        # Meetings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                meeting_time TEXT,
                meeting_link TEXT,
                status TEXT,
                created_at TEXT
            )
        ''')

        # Decisions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                decision TEXT,
                reason TEXT,
                made_at TEXT
            )
        ''')

        # OPTIONAL JOB TABLE (non-breaking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                folder_path TEXT,
                created_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    # =========================
    # SAFE SCHEMA MIGRATION
    # =========================
    def ensure_schema_updates(self):
        """Ensure job_id column exists (non-breaking migration)"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(candidates)")
        columns = [col[1] for col in cursor.fetchall()]

        if "job_id" not in columns:
            print("⚡ Adding job_id column to candidates table...")
            cursor.execute("ALTER TABLE candidates ADD COLUMN job_id TEXT")

        conn.commit()
        conn.close()

    # =========================
    # ADD CANDIDATE (UPDATED)
    # =========================
    def add_candidate(self, name, email, phone, resume_file,
                      match_score, summary, job_id=None):

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO candidates 
                (name, email, phone, resume_file, match_score, summary, status, created_at, application_date, job_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                email,
                phone,
                resume_file,
                match_score,
                summary,
                "NEW",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d"),
                job_id
            ))

            candidate_id = cursor.lastrowid
            conn.commit()
            conn.close()

            print(f"✅ Candidate {name} added (ID: {candidate_id}, Job: {job_id})")
            return candidate_id

        except sqlite3.IntegrityError:
            print(f"⚠️ Candidate {email} already exists")
            return None

        except Exception as e:
            print(f"❌ Error adding candidate: {e}")
            return None

    # =========================
    # STATUS UPDATE
    # =========================
    def update_candidate_status(self, candidate_id, status, match_score=None):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            if match_score is not None:
                cursor.execute('''
                    UPDATE candidates 
                    SET status = ?, match_score = ?
                    WHERE id = ?
                ''', (status, match_score, candidate_id))
            else:
                cursor.execute('''
                    UPDATE candidates 
                    SET status = ?
                    WHERE id = ?
                ''', (status, candidate_id))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error updating candidate: {e}")

    # =========================
    # DECISION LOG
    # =========================
    def log_decision(self, candidate_id, decision, reason):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO decisions (candidate_id, decision, reason, made_at)
                VALUES (?, ?, ?, ?)
            ''', (
                candidate_id,
                decision,
                reason,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error logging decision: {e}")

    # =========================
    # EMAIL LOG
    # =========================
    def log_email(self, candidate_id, email_type, subject, status):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO email_logs (candidate_id, email_type, subject, status, sent_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                candidate_id,
                email_type,
                subject,
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error logging email: {e}")

    # =========================
    # FILTER BY JOB (NEW)
    # =========================
    def get_candidates_by_job(self, job_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM candidates WHERE job_id = ?
                ORDER BY created_at DESC
            ''', (job_id,))

            results = cursor.fetchall()
            conn.close()
            return results

        except Exception as e:
            print(f"❌ Error fetching candidates: {e}")
            return []


# =========================
# GLOBAL INSTANCE (UNCHANGED)
# =========================
db = CandidateDatabase()