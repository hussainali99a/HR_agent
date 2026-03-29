import sqlite3
from datetime import datetime
from config import DATABASE_FILE


class Database:
    def __init__(self):
        self.db_file = DATABASE_FILE
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.execute("PRAGMA foreign_keys = ON")  # 🔥 IMPORTANT
        return conn

    # =========================
    # INIT DATABASE
    # =========================
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # =========================
        # USERS TABLE (NEW)
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                company TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')

        # =========================
        # EMAIL VERIFICATION TOKENS (NEW)
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token TEXT,
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # =========================
        # JOBS TABLE (UPDATED)
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                user_id INTEGER,  -- 🔥 OWNER

                title TEXT,
                profile TEXT,
                description TEXT,
                folder_path TEXT,

                created_at TEXT,

                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # =========================
        # CANDIDATES TABLE (UPDATED)
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                job_id TEXT,
                user_id INTEGER,  -- 🔥 OWNER

                name TEXT,
                email TEXT,
                phone TEXT,

                resume_file TEXT,
                file_hash TEXT UNIQUE,

                match_score REAL,
                status TEXT,

                summary TEXT,

                skills TEXT,
                experience INTEGER,
                linkedin TEXT,

                created_at TEXT,
                application_date TEXT,

                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # =========================
        # DECISIONS TABLE
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                candidate_id INTEGER,
                decision TEXT,
                reason TEXT,
                made_at TEXT,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # =========================
        # EMAIL LOGS
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                user_id INTEGER,
                email_type TEXT,
                subject TEXT,
                status TEXT,
                sent_at TEXT,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # =========================
        # MEETINGS TABLE (ENHANCED)
        # =========================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                candidate_id INTEGER,
                hr_id INTEGER,  -- 🔥 WHO SCHEDULED

                meeting_time TEXT,
                meeting_link TEXT,
                status TEXT,

                created_at TEXT,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
                FOREIGN KEY(hr_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

        print("✅ Database initialized (auth + ATS ready)")

    # =========================
    # USER OPERATIONS
    # =========================
    def create_user(self, name, company, email, password):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (name, company, email, password, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, company, email, password, datetime.now()))

        user_id = cur.lastrowid

        conn.commit()
        conn.close()

        return user_id

    def get_user(self, email):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()

        conn.close()
        return user

    def verify_user(self, user_id):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("UPDATE users SET is_verified=1 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

    # =========================
    # JOB OPERATIONS
    # =========================
    def add_job(self, job_id, user_id, title, profile, description, folder_path):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO jobs (id, user_id, title, profile, description, folder_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            user_id,
            title,
            profile,
            description,
            folder_path,
            datetime.now()
        ))

        conn.commit()
        conn.close()

    # =========================
    # CANDIDATE OPERATIONS
    # =========================
    def add_candidate(
        self,
        job_id,
        user_id,
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
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO candidates (
                    job_id, user_id,
                    name, email, phone,
                    resume_file, file_hash,
                    match_score, status,
                    summary, skills, experience, linkedin,
                    created_at, application_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, user_id,
                name, email, phone,
                resume_file, file_hash,
                match_score, status,
                summary, skills, experience, linkedin,
                datetime.now(),
                datetime.now().date()
            ))

            candidate_id = cur.lastrowid
            conn.commit()
            return candidate_id

        except sqlite3.IntegrityError:
            print("⚠️ Duplicate resume skipped")
            return None

        finally:
            conn.close()

    # =========================
    # INTERVIEW SCHEDULING
    # =========================
    def schedule_interview(self, candidate_id, hr_id, meeting_link, time):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO meetings (candidate_id, hr_id, meeting_link, meeting_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            hr_id,
            meeting_link,
            time,
            "SCHEDULED",
            datetime.now()
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

    def update_candidate_status(self, candidate_id, status, match_score=None):
        """Update candidate status"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            if match_score is not None:
                cursor.execute('''
                    UPDATE candidates 
                    SET status = ?
                    WHERE id = ?
                ''', (status, candidate_id))
            

            conn.commit()
            conn.close()
            print(f"✅ Candidate {candidate_id} status updated to: {status}")
            

        except Exception as e:
            print(f"❌ Error updating candidate status: {e}")
    
    def log_decision(self, user_id, candidate_id, decision, reason):
        """Log the decision made for a candidate"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO decisions (user_id, candidate_id, decision, reason, made_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                candidate_id,
                decision,
                reason,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        

            conn.commit()
            conn.close()
            print(f"✅ Decision logged for candidate {candidate_id}: {decision}")
            

        except Exception as e:
            print(f"❌ Error logging decision: {e}")

    def log_email(self, user_id,candidate_id, email_type, subject, status):
        """Log email sent to candidate"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            

            cursor.execute('''
                INSERT INTO email_logs (user_id,candidate_id, email_type, subject, status, sent_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
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
# GLOBAL INSTANCE
# =========================
db = Database()