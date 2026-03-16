"""
Configuration Validation & System Test
Run this to verify everything is set up correctly before running the main agent
"""

import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("🔍 HR RECRUITMENT AGENT - SYSTEM VALIDATION")
print("="*70)

def check_python_version():
    """Check Python version"""
    print("\n📌 Python Version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} (Need 3.8+)")
        return False

def check_file_structure():
    """Check if required files exist"""
    print("\n📌 File Structure...")
    
    required_files = [
        'main_agent.py',
        'config.py',
        'database.py',
        'resume_parser.py',
        'candidate_matcher.py',
        'email_sender.py',
        'meet_scheduler.py',
        'dashboard.py'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (MISSING)")
            missing.append(file)
    
    return len(missing) == 0

def check_folders():
    """Check if required folders exist"""
    print("\n📌 Folder Structure...")
    
    required_folders = ['resumes']
    
    all_ok = True
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"   ✅ {folder}/")
        else:
            print(f"   ❌ {folder}/ (MISSING)")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check .env configuration file"""
    print("\n📌 Environment Configuration (.env)...")
    
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        print("   💡 Create from .env.example:")
        print("      1. Copy .env.example to .env")
        print("      2. Fill in your Gmail and Google details")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        checks = {
            'GMAIL_ADDRESS': os.getenv('GMAIL_ADDRESS'),
            'GMAIL_PASSWORD': os.getenv('GMAIL_PASSWORD'),
            'GOOGLE_CREDENTIALS_FILE': os.getenv('GOOGLE_CREDENTIALS_FILE'),
        }
        
        all_set = True
        for key, value in checks.items():
            if value:
                masked_value = value[:10] + '...' if len(str(value)) > 10 else value
                print(f"   ✅ {key} = {masked_value}")
            else:
                print(f"   ❌ {key} (NOT SET)")
                all_set = False
        
        return all_set
    
    except Exception as e:
        print(f"   ❌ Error reading .env: {e}")
        return False

def check_google_credentials():
    """Check if Google credentials file exists"""
    print("\n📌 Google Credentials...")
    
    cred_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    if not os.path.exists(cred_file):
        print(f"   ❌ {cred_file} not found")
        print("   💡 Download from Google Cloud Console:")
        print("      1. Go to console.cloud.google.com")
        print("      2. Credentials → Service Account → KEYS")
        print("      3. Create JSON key")
        print(f"      4. Save as {cred_file}")
        return False
    
    print(f"   ✅ {cred_file} found")
    
    try:
        import json
        with open(cred_file) as f:
            creds = json.load(f)
        
        if 'type' in creds and 'client_email' in creds:
            print(f"      Email: {creds['client_email']}")
            return True
        else:
            print("   ❌ credentials.json format incorrect")
            return False
    
    except Exception as e:
        print(f"   ❌ Error reading credentials: {e}")
        return False

def check_packages():
    """Check if required Python packages are installed"""
    print("\n📌 Python Packages...")
    
    required_packages = {
        'dotenv': 'python-dotenv',
        'pdfplumber': 'pdfplumber',
        'sklearn': 'scikit-learn',
        'google.auth': 'google-auth-oauthlib',
        'googleapiclient': 'google-api-python-client',
        'pandas': 'pandas',
        'streamlit': 'streamlit',
    }
    
    all_installed = True
    for package, install_name in required_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {install_name}")
        except ImportError:
            print(f"   ❌ {install_name} (NOT INSTALLED)")
            print(f"      Run: pip install {install_name}")
            all_installed = False
    
    return all_installed

def check_job_description():
    """Check if job description exists"""
    print("\n📌 Job Description...")
    
    job_file = 'resumes/job_description.txt'
    
    if not os.path.exists(job_file):
        print(f"   ❌ {job_file} not found")
        print("   💡 Create it:")
        print('      1. Create file: resumes/job_description.txt')
        print("      2. Write your job requirements")
        print("      3. Save and close")
        return False
    
    try:
        with open(job_file) as f:
            content = f.read()
        
        if len(content) > 50:
            print(f"   ✅ {job_file} ({len(content)} characters)")
            return True
        else:
            print(f"   ⚠️  {job_file} seems too short")
            return False
    
    except Exception as e:
        print(f"   ❌ Error reading job description: {e}")
        return False

def check_resume_files():
    """Check if there are any resumes"""
    print("\n📌 Resume Files...")
    
    if not os.path.exists('resumes'):
        print("   ❌ resumes/ folder not found")
        return False
    
    pdf_files = [f for f in os.listdir('resumes') if f.endswith('.pdf')]
    
    if len(pdf_files) == 0:
        print("   ⚠️  No PDF files found in resumes/")
        print("   💡 Add candidate PDFs to resumes/ folder")
        return True  # Not critical, can add later
    
    print(f"   ✅ Found {len(pdf_files)} resume(s):")
    for pdf in pdf_files:
        print(f"      - {pdf}")
    
    return True

def test_config_import():
    """Test if config module imports correctly"""
    print("\n📌 Configuration Module...")
    
    try:
        from config import validate_config
        result = validate_config()
        if result:
            print("   ✅ Config validation passed")
            return True
        else:
            print("   ❌ Config validation failed")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_database():
    """Test database setup"""
    print("\n📌 Database...")
    
    try:
        from database import db
        candidates = db.get_all_candidates()
        print(f"   ✅ Database initialized (Currently {len(candidates)} candidates)")
        return True
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_email():
    """Test email configuration"""
    print("\n📌 Email System...")
    
    try:
        from email_sender import email_sender
        if email_sender.validate_credentials():
            print("   ✅ Email credentials valid")
            return True
        else:
            print("   ❌ Email credentials invalid")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_google_calendar():
    """Test Google Calendar connection"""
    print("\n📌 Google Calendar Service...")
    
    try:
        from meet_scheduler import scheduler
        if scheduler.service is not None:
            print("   ✅ Google Calendar service initialized")
            return True
        else:
            print("   ❌ Google Calendar service failed")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all checks"""
    
    checks = [
        ("Python Version", check_python_version),
        ("File Structure", check_file_structure),
        ("Folder Structure", check_folders),
        ("Environment Configuration", check_env_file),
        ("Google Credentials", check_google_credentials),
        ("Python Packages", check_packages),
        ("Job Description", check_job_description),
        ("Resume Files", check_resume_files),
        ("Config Module", test_config_import),
        ("Database", test_database),
        ("Email System", test_email),
        ("Google Calendar", test_google_calendar),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n⚠️  Unexpected error in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! You're ready to run the agent!")
        print("\n   Command: python main_agent.py")
        return True
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("   Fix the issues, then run this script again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
