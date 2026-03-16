"""
Centralized Configuration Management
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===== GMAIL SETTINGS =====
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")

# ===== GOOGLE CALENDAR SETTINGS =====
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# ===== OPENAI SETTINGS =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ===== DATABASE SETTINGS =====
DATABASE_FILE = os.getenv("DATABASE_FILE", "candidates.db")
RESUME_FOLDER = os.getenv("RESUME_FOLDER", "resumes")

# ===== JOB DESCRIPTION SETTINGS =====
JOB_DESCRIPTION_FILE = os.getenv("JOB_DESCRIPTION_FILE", "resumes/job_description.txt")

# ===== INTERVIEW SETTINGS =====
INTERVIEW_DURATION_MINUTES = int(os.getenv("INTERVIEW_DURATION_MINUTES", "30"))
INTERVIEW_TIMEZONE = os.getenv("INTERVIEW_TIMEZONE", "Asia/Kolkata")

# ===== SCORING THRESHOLDS =====
SCORE_ACCEPT_THRESHOLD = float(os.getenv("SCORE_ACCEPT_THRESHOLD", "0.70"))  # 70%
SCORE_HOLD_THRESHOLD = float(os.getenv("SCORE_HOLD_THRESHOLD", "0.50"))     # 50%
# Below 50% = Reject

# ===== EMAIL TEMPLATES =====
EMAIL_SIGNATURE = """

Best Regards,
AI Recruitment Team
HR Department"""

# Validation function to check if all required settings are present
def validate_config():
    """Check if all required settings are configured"""
    errors = []
    
    if not GMAIL_ADDRESS:
        errors.append("❌ GMAIL_ADDRESS not set in .env file")
    if not GMAIL_PASSWORD:
        errors.append("❌ GMAIL_PASSWORD not set in .env file")
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        errors.append(f"❌ Google credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
    
    if errors:
        print("⚠️  CONFIGURATION ERRORS DETECTED:\n")
        for error in errors:
            print(error)
        print("\n👉 Please check the SETUP_GUIDE.md for instructions")
        return False
    
    print("✅ Configuration validated successfully!")
    return True

if __name__ == "__main__":
    # Test configuration
    validate_config()
    print("\nCurrent Settings:")
    print(f"  Gmail: {GMAIL_ADDRESS}")
    print(f"  Database: {DATABASE_FILE}")
    print(f"  Resume Folder: {RESUME_FOLDER}")
    print(f"  Accept Threshold: {SCORE_ACCEPT_THRESHOLD * 100}%")
