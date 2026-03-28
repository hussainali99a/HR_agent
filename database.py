import sqlite3
from datetime import datetime
from config import DATABASE_FILE


class Database:
    def __init__(self):
        self.db_file = DATABASE_FILE
        self.init_db()

    # =========================
    # INIT DATABASE
    # =========================
    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # =========================
        # JOBS TABLE
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                profile TEXT,
                description TEXT,
                folder_path TEXT,
                created_at TEXT
            )
        ''')

        # =========================
        # CANDIDATES TABLE
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,

                name TEXT,
                email TEXT,
                phone TEXT,

                resume_file TEXT,
                file_hash TEXT,

                match_score REAL,
                status TEXT,

                summary TEXT,

                skills TEXT,
                experience INTEGER,
                linkedin TEXT,

                created_at TEXT,
                application_date TEXT,

                FOREIGN KEY(job_id) REFERENCES jobs(id)
            )
        ''')

        # =========================
        # DECISIONS TABLE
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                decision TEXT,
                reason TEXT,
                made_at TEXT,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
        ''')

        # =========================
        # EMAIL LOGS
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                email_type TEXT,
                subject TEXT,
                status TEXT,
                sent_at TEXT,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
        ''')

        # =========================
        # MEETINGS
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                meeting_time TEXT,
                meeting_link TEXT,
                status TEXT,
                created_at TEXT,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
        ''')

        conn.commit()
        conn.close()

        print("✅ Fresh database initialized")

    # =========================
    # JOB OPERATIONS
    # =========================
    def add_job(self, job_id, title, profile, description, folder_path):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO jobs (id, title, profile, description, folder_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            title,
            profile,
            description,
            folder_path,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

    def get_jobs(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        jobs = cursor.fetchall()

        conn.close()
        return jobs

    # =========================
    # CANDIDATE OPERATIONS
    # =========================
    def add_candidate(
        self,
        job_id,
        name,
        email,
        phone,
        resume_file,
        file_hash,
        match_score,
        summary,
        skills,
        experience,
        linkedin,
        status="NEW"
    ):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO candidates (
                job_id,
                name,
                email,
                phone,
                resume_file,
                file_hash,
                match_score,
                status,
                summary,
                skills,
                experience,
                linkedin,
                created_at,
                application_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            name,
            email,
            phone,
            resume_file,
            file_hash,
            match_score,
            status,
            summary,
            skills,
            experience,
            linkedin,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d")
        ))

        candidate_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return candidate_id

    # =========================
    # UPDATE STATUS
    # =========================
    def update_candidate_status(self, candidate_id, status, score=None):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        if score is not None:
            cursor.execute('''
                UPDATE candidates
                SET status=?, match_score=?
                WHERE id=?
            ''', (status, score, candidate_id))
        else:
            cursor.execute('''
                UPDATE candidates
                SET status=?
                WHERE id=?
            ''', (status, candidate_id))

        conn.commit()
        conn.close()

    # =========================
    # FETCH BY JOB
    # =========================
    def get_candidates_by_job(self, job_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM candidates
            WHERE job_id=?
            ORDER BY match_score DESC
        ''', (job_id,))

        data = cursor.fetchall()
        conn.close()
        return data

    # =========================
    # DECISION LOG
    # =========================
    def log_decision(self, candidate_id, decision, reason):
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

    # =========================
    # EMAIL LOG
    # =========================
    def log_email(self, candidate_id, email_type, subject, status):
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

    # =========================
    # DUPLICATE CHECK
    # =========================
    def is_duplicate(self, file_hash):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM candidates WHERE file_hash=?",
            (file_hash,)
        )

        exists = cursor.fetchone() is not None

        conn.close()
        return exists


# =========================
# GLOBAL INSTANCE
# =========================
db = Database()