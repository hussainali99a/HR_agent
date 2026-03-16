"""
Database Management for Candidate Information
Stores all candidate data, scores, and decisions
"""

import sqlite3
from datetime import datetime
import json
import os
from config import DATABASE_FILE

class CandidateDatabase:
    """Manages all database operations for candidates"""
    
    def __init__(self):
        """Initialize database connection"""
        self.db_file = DATABASE_FILE
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Candidates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                resume_file TEXT,
                job_title TEXT,
                application_date TEXT,
                status TEXT,
                match_score REAL,
                summary TEXT,
                created_at TEXT
            )
        ''')
        
        # Email logs table
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
        
        # Meeting table
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
        
        # Decision log table
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
        
        conn.commit()
        conn.close()
        print("✅ Database tables created/verified")
    
    def add_candidate(self, name, email, phone, resume_file, match_score, summary):
        """Add a new candidate to database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO candidates 
                (name, email, phone, resume_file, match_score, summary, status, created_at, application_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, email, phone, resume_file, 
                match_score, summary, "NEW", 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d")
            ))
            
            candidate_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Candidate {name} added to database (ID: {candidate_id})")
            return candidate_id
            
        except sqlite3.IntegrityError:
            print(f"⚠️  Candidate {email} already exists in database")
            return None
        except Exception as e:
            print(f"❌ Error adding candidate: {e}")
            return None
    
    def update_candidate_status(self, candidate_id, status, match_score=None):
        """Update candidate status"""
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
            print(f"✅ Candidate {candidate_id} status updated to: {status}")
            
        except Exception as e:
            print(f"❌ Error updating candidate status: {e}")
    
    def log_decision(self, candidate_id, decision, reason):
        """Log the decision made for a candidate"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO decisions (candidate_id, decision, reason, made_at)
                VALUES (?, ?, ?, ?)
            ''', (
                candidate_id, decision, reason,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Decision logged for candidate {candidate_id}: {decision}")
            
        except Exception as e:
            print(f"❌ Error logging decision: {e}")
    
    def log_email(self, candidate_id, email_type, subject, status):
        """Log email sent to candidate"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO email_logs (candidate_id, email_type, subject, status, sent_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                candidate_id, email_type, subject, status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error logging email: {e}")
    
    def log_meeting(self, candidate_id, meeting_time, meeting_link, status="SCHEDULED"):
        """Log meeting scheduled for candidate"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meetings (candidate_id, meeting_time, meeting_link, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                candidate_id, meeting_time, meeting_link, status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Meeting logged for candidate {candidate_id}")
            
        except Exception as e:
            print(f"❌ Error logging meeting: {e}")
    
    def get_candidate(self, candidate_id):
        """Get candidate details by ID"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"❌ Error fetching candidate: {e}")
            return None
    
    def get_all_candidates(self):
        """Get all candidates from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM candidates ORDER BY created_at DESC')
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"❌ Error fetching candidates: {e}")
            return []
    
    def get_candidates_by_status(self, status):
        """Get candidates filtered by status"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM candidates WHERE status = ? ORDER BY match_score DESC', (status,))
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"❌ Error fetching candidates by status: {e}")
            return []
    
    def export_to_csv(self, filename="candidates_export.csv"):
        """Export candidate data to CSV"""
        try:
            import pandas as pd
            
            conn = sqlite3.connect(self.db_file)
            df = pd.read_sql_query('SELECT * FROM candidates', conn)
            conn.close()
            
            df.to_csv(filename, index=False)
            print(f"✅ Data exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")

# Global database instance
if not os.path.exists(DATABASE_FILE):
    db = CandidateDatabase()
else:
    db = CandidateDatabase()

if __name__ == "__main__":
    # Test the database
    print("Testing database...")
    test_db = CandidateDatabase()
    
    # Show all candidates
    candidates = test_db.get_all_candidates()
    print(f"\nTotal candidates in database: {len(candidates)}")
