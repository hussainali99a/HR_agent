# 🤖 AI HR Recruitment Agent

An intelligent, fully-automated recruitment system that evaluates resumes, schedules Google Meet interviews with passcodes, and sends professional emails to candidates using AI matching.

**Total Setup Time: 45-60 minutes (first time only)**

---

## 📋 Table of Contents

1. [What It Does](#-what-it-does)
2. [Quick Overview](#-quick-overview)
3. [Complete Setup Guide](#-complete-setup-guide)
4. [Getting Started](#-getting-started)
5. [Running the Agent](#-running-the-agent)
6. [Configuration](#-configuration)
7. [Troubleshooting](#-troubleshooting)
8. [File Reference](#-file-reference)

---

## ✨ What It Does

This AI-powered recruitment agent automates the entire hiring workflow:

1. **📥 Receives Applications** - Process submitted resumes (PDF/DOCX)
2. **🤖 Analyzes Resumes** - AI matches resume skills to job requirements
3. **🎯 Makes Decisions** - Automatically accepts, rejects, or flags for review
4. **📧 Sends Emails** - Professional accept/reject/hold notifications
5. **📅 Schedules Google Meet** - Creates real meeting links with passcodes
6. **📊 Tracks Everything** - Database logs all decisions, meetings, and emails

---

## 🚀 Quick Overview

### The Flow:
```
Job Posted → Candidates Apply → Run Agent → AI Scores Each Resume 
→ Auto Decision (Accept/Reject/Hold) → Emails Sent → Meetings Scheduled 
→ View Dashboard
```

### What You'll See:
- ✅ Candidates automatically scored (0-100%)
- ✅ Professional emails sent instantly
- ✅ Google Meet links created
- ✅ All data saved to database
- ✅ Beautiful dashboard with analytics

### Scoring Breakdown:
- **90-100%** → ✅ **ACCEPT** (Auto-approved)
- **70-89%** → ✅ **ACCEPT** (Auto-approved)
- **50-69%** → ⏳ **HOLD** (Needs human review)
- **<50%** → ❌ **REJECT** (Auto-rejected)

---

## 📥 System Requirements

### Must Have:
- **Python 3.9+** (Download from [python.org](https://www.python.org/downloads/))
- **Gmail Account** (with 2-Step Verification enabled)
- **Google Account** (for Calendar and Meet - can be same as Gmail)
- **Candidate Resume Files** (PDF or DOCX format)

### Setup Time:
- Gmail + Google setup: 15 minutes
- Python environment: 10 minutes
- Configuration: 5 minutes
- Verification: 5 minutes
- **Total: 35-45 minutes**

---

## 📝 Complete Setup Guide

### ✅ STEP 1: Gmail Setup (5 minutes)

#### Enable 2-Step Verification:
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification" on the left
3. Click it and follow instructions (need your phone)
4. Once enabled, go back to Security page

#### Get App Password:
1. Under Security, find **"App passwords"**
2. Select:
   - **App**: Mail
   - **Device**: Windows Computer
3. Google gives you a **16-character password** (e.g.: `qwer asdf zxcv qwerty`)
4. **SAVE THIS** - You'll need it in Step 3

**You now have:**
- Email: `yourname@gmail.com`
- App Password: `qwer asdf zxcv qwerty` (16 characters with spaces)

---

### ✅ STEP 2: Google OAuth2 Setup (10 minutes)

This allows the agent to create real Google Meet links and schedule calendar events.

#### Create Google Cloud Project:
1. Visit: https://console.cloud.google.com
2. At the top, click the **project selector** dropdown
3. Click **NEW PROJECT**
4. Name it: `HR_Agent`
5. Click **CREATE** and wait for completion

#### Enable Required APIs:
1. In the left menu, click **APIs & Services** → **Library**
2. Search for: `Google Calendar API`
3. Click it and select **ENABLE**
4. Go back to Library
5. Search for: `Google Meet API`
6. Click it and select **ENABLE**

#### Configure OAuth2 Consent Screen:
1. Left menu: **APIs & Services** → **OAuth consent screen**
2. Select: **External** (for testing)
3. Click **CREATE**
4. Fill in the form:
   - **App name**: `HR Recruitment Agent`
   - **Support email**: Your email
   - **Developer contact**: Your email
5. Click **SAVE AND CONTINUE**
6. On **Scopes** page, click **ADD OR REMOVE SCOPES**
7. Search and add:
   - `https://www.googleapis.com/auth/calendar` (Calendar)
   - `https://www.googleapis.com/auth/userinfo.email` (Email)
8. Click **UPDATE** → **SAVE AND CONTINUE**
9. On **Test Users** page:
   - Click **ADD USERS**
   - Add your email address (e.g., `yourname@gmail.com`)
   - Click **ADD**
10. Scroll down and click **SAVE AND CONTINUE**

#### Create OAuth2 Credentials:
1. Left menu: **APIs & Services** → **Credentials**
2. Click **CREATE CREDENTIALS** → **OAuth 2.0 Client IDs**
3. If prompted, first click **Configure Consent Screen** and complete above steps
4. Select type: **Desktop application**
5. Name it: `HR Agent Main`
6. Click **CREATE**
7. A dialog appears with your credentials
8. Click **DOWNLOAD JSON**
9. **Rename the file to**: `oauth_credentials.json`
10. **Move it to**: `d:\HR_agent\` folder (same level as main_agent.py)

---

### ✅ STEP 3: Create Configuration File (2 minutes)

1. Open **Notepad**
2. Copy this configuration template (replace YOUR info):

```env
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_PASSWORD=your_16_char_app_password_here

GOOGLE_OAUTH_CREDENTIALS=oauth_credentials.json

DATABASE_FILE=candidates.db
RESUME_FOLDER=resumes
JOB_DESCRIPTION_FILE=resumes/job_description.txt

INTERVIEW_DURATION_MINUTES=30
INTERVIEW_TIMEZONE=Asia/Kolkata

SCORE_ACCEPT_THRESHOLD=0.70
SCORE_HOLD_THRESHOLD=0.50
```

3. **Save as `.env`** in `d:\HR_agent\` folder
   - Click **File** → **Save As**
   - Filename: `.env`
   - Save as type: **All Files** (not .txt!)
   - Location: `d:\HR_agent\`
   - Click **Save**

⚠️ **IMPORTANT:** This file contains secrets. Never share or commit it!

---

### ✅ STEP 4: Install Python Packages (3 minutes)

1. Open **PowerShell**
2. Navigate to folder:
   ```powershell
   cd d:\HR_agent
   ```

3. Create virtual environment (recommended):
   ```powershell
   python -m venv env-hr-agent
   env-hr-agent\Scripts\activate
   ```

4. Install all packages:
   ```powershell
   pip install -r requirements.txt
   ```

   Or install individually:
   ```powershell
   pip install openai pandas streamlit pdfplumber scikit-learn
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   pip install python-dotenv plotly python-docx
   ```

---

### ✅ STEP 5: Verify Setup

Run validation:
```powershell
python validate_setup.py
```

You should see:
```
✅ Configuration validated successfully!
✅ Gmail service ready
✅ Google Calendar service ready
✅ Database ready
```

If any errors, see **Troubleshooting** section below.

---

## 🎯 Getting Started

### Folder Structure

Your project folder should look like this:

```
d:\HR_agent\
├── .env                          ← Your config (KEEP SECRET!)
├── oauth_credentials.json        ← Google OAuth2 key (KEEP SECRET!)
├── requirements.txt
├── main_agent.py                 ← MAIN PROGRAM
├── dashboard.py                  ← View results
├── google_auth.py                ← OAuth2 handler (new)
├── config.py
├── database.py
├── resume_parser.py
├── candidate_matcher.py
├── email_sender.py
├── meet_scheduler.py
├── validate_setup.py
│
├── candidates.db                 ← Created automatically
├── candidates_export.csv         ← Created automatically
│
└── resumes/
    ├── job_description.txt       ← Your job requirements
    ├── candidate1.pdf
    └── candidate2.pdf
```

### Create Job Description

1. Open Notepad
2. Write your job description:

```
We are looking for a Senior Python Developer

Requirements:
- 5+ years of Python experience
- Strong Django framework knowledge
- React.js frontend skills
- AWS cloud experience
- SQL and database knowledge

Nice to Have:
- Machine Learning experience
- Docker and Kubernetes
- Agile/Scrum certification

Responsibilities:
- Build and maintain APIs
- Code reviews
- Team collaboration
- Technical documentation
```

3. Save as: **`job_description.txt`** in **`resumes/`** folder

### Add Candidate Resumes

1. Get candidate PDF or DOCX files
2. Place them in: **`resumes/`** folder
3. Name them: `John_Doe.pdf`, `Jane_Smith.pdf`, etc.

**Supported Formats:**
- `.pdf` (text-based, not scanned images)
- `.docx` (Microsoft Word documents)
- `.doc` (older Word documents)

---

## 🎬 Running the Agent

### Method 1: PowerShell

```powershell
cd d:\HR_agent
env-hr-agent\Scripts\activate
python main_agent.py
```

### Method 2: Batch File (Double-Click)

Create a file named `RUN_AGENT.bat`:

```batch
@echo off
cd d:\HR_agent
call env-hr-agent\Scripts\activate
python main_agent.py
pause
```

Then just double-click it!

### What You'll See:

```
✅ Configuration validated successfully!
✅ Google OAuth2 service initialized
✅ Job description loaded (3441 characters)

============================================================
🤖 HR RECRUITMENT AGENT STARTING
============================================================

📂 Found 2 resume(s) to process

============================================================
Processing: John_Doe.pdf
============================================================
✅ Resume parsed: John_Doe.pdf (5234 characters)
📧 Email: john.doe@email.com

📊 MATCH ANALYSIS:
   Score: 78.5%
   Status: ACCEPT
   Reason: Strong match - 5+ years experience, Django expert

🎯 DECISION: ACCEPT (78.5%)

✅ Acceptance email sent to john.doe@email.com
✅ Interview scheduled for John Doe
   📅 Date/Time: 2026-03-17 10:00 AM IST
   🔗 Meet Link: https://meet.google.com/abc-defg-hij
   🔐 Passcode: 123456
   ⏱️ Duration: 30 minutes

✅ Meeting logged to database

============================================================
```

---

## 📊 Viewing Results

### View Dashboard

```powershell
# New PowerShell window
cd d:\HR_agent
env-hr-agent\Scripts\activate
streamlit run dashboard.py
```

Browser opens showing:
- ✅ **Candidate Status** - Approved/Rejected/Under Review
- 📈 **Analytics** - Score trends and charts
- 📧 **Email Logs** - All communications
- 👥 **Details** - Full candidate information

### Data Files Created

After running:
- **candidates.db** - SQLite database with all candidate data
- **candidates_export.csv** - Spreadsheet format

---

## ⚙️ Configuration

### Email Templates

The system sends professional emails automatically:

**Acceptance Email:**
```
Dear [Candidate Name],

Congratulations! We are pleased to inform you that your 
application for the position of Senior Python Developer 
has been shortlisted.

📅 Interview Details:
Date & Time: March 17, 2026 at 10:00 AM IST
Interview Link: https://meet.google.com/xxx-xxxx-xxx
Duration: 30 minutes
Type: Google Meet (Video Call)

Please join 5 minutes early.

Best Regards,
AI Recruitment Team
HR Department
```

**Rejection Email:**
```
Dear [Candidate Name],

Thank you for your interest in the Senior Python Developer 
position at our organization.

After careful consideration of your profile and qualifications, 
we have decided to move forward with other candidates whose 
skills more closely match our current requirements.

We encourage you to apply for future positions that may be 
a better fit for your profile.

We wish you the very best in your career!

Best Regards,
AI Recruitment Team
HR Department
```

### Scoring Configuration

In `.env` file, customize thresholds:

```env
# Accept threshold (default 70% = 0.70)
SCORE_ACCEPT_THRESHOLD=0.70

# Hold threshold (default 50% = 0.50)
# Below this = Reject
SCORE_HOLD_THRESHOLD=0.50
```

### Interview Settings

```env
INTERVIEW_DURATION_MINUTES=30
INTERVIEW_TIMEZONE=Asia/Kolkata
```

Supported timezones: `America/New_York`, `Europe/London`, `Asia/Tokyo`, etc.

---

## 🚨 Troubleshooting

### Issue: "Module not found"

**Cause:** Virtual environment not activated or packages not installed

**Fix:**
```powershell
cd d:\HR_agent
env-hr-agent\Scripts\activate
pip install -r requirements.txt
```

---

### Issue: "GMAIL_ADDRESS not set in .env"

**Cause:** `.env` file missing or incomplete

**Fix:**
1. Check `.env` exists in `d:\HR_agent\`
2. Verify it has all required variables
3. Recreate if necessary (see Step 3 above)

---

### Issue: "oauth_credentials.json not found"

**Cause:** OAuth2 JSON key missing or in wrong location

**Fix:**
1. Download fresh JSON from Google Cloud Console
2. Rename EXACTLY to: `oauth_credentials.json`
3. Place in `d:\HR_agent\` (same level as main_agent.py)
4. Verify it's valid JSON (can open in text editor)

---

### Issue: "Access blocked: HR_agent has not completed the Google verification process"

**Cause:** Your app is unverified and Gmail account not added as test user

**Fix:**
1. Go to Google Cloud Console
2. Navigate to **OAuth consent screen** (left menu)
3. Scroll down to **Test users** section
4. Click **ADD USERS**
5. Add your Gmail address: `your_email@gmail.com`
6. Click **ADD**
7. Save and return to consent screen

---

### Issue: "No resume files found"

**Cause:** Files in wrong location or unsupported format

**Fix:**
1. Check files are in `resumes/` folder (not subfolders)
2. Verify extensions: `.pdf`, `.docx`, or `.doc`
3. No shortcuts (.lnk) - use actual file copies
4. Filenames without special characters

---

### Issue: "No text extracted from PDF"

**Cause:** PDF is a scanned image, not text-based

**Fix:**
1. Use online tool (ilovepdf.com) to convert
2. Or export PDF again from original document
3. Or save as DOCX instead and use that

---

### Issue: "Email credential error"

**Cause:** App password incorrect or 2-Step not enabled

**Fix:**
1. Verify 2-Step Verification is ON at myaccount.google.com
2. Check app password is exactly right (16 chars with spaces)
3. Ensure it's an app password, not your main Gmail password
4. Generate new app password if needed at myaccount.google.com/apppasswords

---

### Issue: "Calendar event failed to create"

**Cause:** OAuth2 token expired or invalid permissions

**Fix:**
1. Delete `token.pickle` file if it exists
2. Run script again - it will request new authorization
3. Verify test user added to Google Cloud OAuth consent screen
4. Check "Calendar" scope is added in OAuth consent screen

---

### Issue: "ServiceAccountCredentials error"

**Cause:** Old service account credentials still being used

**Fix:**
1. Delete any `credentials.json` file
2. Ensure `.env` uses `oauth_credentials.json`
3. Update `meet_scheduler.py` to use OAuth2 (already done in current version)
4. Run validation: `python validate_setup.py`

---

### Issue: Database errors

**Cause:** Database corrupted or locked

**Fix:**
```powershell
del candidates.db
python main_agent.py
```

---

## 📁 File Reference

### Core Application

| File | Purpose |
|------|---------|
| `main_agent.py` | Main program - processes resumes, makes decisions, schedules meetings |
| `dashboard.py` | Streamlit dashboard - view results and analytics |
| `validate_setup.py` | Validation script - checks configuration and dependencies |
| `requirements.txt` | Python package dependencies |
| `config.py` | Configuration management and .env loading |
| `database.py` | SQLite database operations and logging |

### Processing Modules

| File | Purpose |
|------|---------|
| `resume_parser.py` | Extract text from PDF/DOCX/DOC files |
| `candidate_matcher.py` | AI scoring - match resume skills to job requirements |
| `email_sender.py` | Gmail integration - send acceptance/rejection emails |
| `meet_scheduler.py` | Google Calendar/Meet - schedule interviews with passcodes |
| `google_auth.py` | OAuth2 token management and authentication |

### Configuration (Keep Secret!)

| File | Purpose |
|------|---------|
| `.env` | Your credentials (Gmail, Google OAuth2, settings) |
| `oauth_credentials.json` | Google OAuth2 credentials (download from Cloud Console) |

### Data Files (Created Automatically)

| File | Purpose |
|------|---------|
| `candidates.db` | SQLite database with all candidate data |
| `candidates_export.csv` | CSV export of candidate information |
| `token.pickle` | OAuth2 token cache (auto-created, can be deleted) |

---

## 🔑 Environment Variables Reference

```env
# Gmail (For sending emails)
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_PASSWORD=your_16_character_app_password_here

# Google OAuth2 (For Calendar and Meet scheduling)
GOOGLE_OAUTH_CREDENTIALS=oauth_credentials.json

# Database (Where candidate data is stored)
DATABASE_FILE=candidates.db
RESUME_FOLDER=resumes
JOB_DESCRIPTION_FILE=resumes/job_description.txt

# Interview Settings
INTERVIEW_DURATION_MINUTES=30
INTERVIEW_TIMEZONE=Asia/Kolkata

# Scoring Thresholds (0 to 1 scale)
SCORE_ACCEPT_THRESHOLD=0.70      # 70% or above = Accept
SCORE_HOLD_THRESHOLD=0.50        # 50-70% = Hold (review)
                                 # Below 50% = Reject
```

---

## 📊 How Scoring Works

### The AI Matching Process:

1. **Extract Keywords** 🔗
   - Skills from job description
   - Skills from resume

2. **Calculate Similarity** 📊
   - Uses TF-IDF vectorization
   - Calculates cosine similarity
   - Scales to 0-100%

3. **Make Decision** 🎯
   - Score ≥ 70% → ACCEPT
   - 50-70% → HOLD
   - Score < 50% → REJECT

4. **Generate Report** 📄
   - Matching keywords
   - Missing keywords
   - Decisions reasoning

### Example Scores:

- **92%** - All requirements + extra relevant skills
- **78%** - Good fit but missing 1-2 nice-to-haves
- **64%** - Has most skills but less experience
- **38%** - Some skills but missing key requirements

---

## 🎯 Workflow Summary

### Day 1 - Initial Setup
```
✓ Gmail configuration
✓ Google Calendar setup
✓ .env file creation
✓ Python packages installed
✓ Validation passed
```

### Day 2 - Prepare Data
```
✓ Create job_description.txt
✓ Add candidate PDFs to resumes/ folder
✓ Run validation again
```

### Day 3 - Run Agent
```
✓ Execute: python main_agent.py
✓ Watch as resumes are processed
✓ Emails sent automatically
✓ Meetings scheduled
```

### Day 4 - Review Results
```
✓ Run: streamlit run dashboard.py
✓ View candidate statuses
✓ Check analytics
✓ Review interview links
```

### Days 5+ - Conduct Interviews
```
✓ Join Google Meet links
✓ Conduct interviews
✓ Update candidate status
✓ Export data as needed
```

---

## 💡 Pro Tips

### For Best Results:

1. **Job Description** - Be specific about requirements
2. **Resume Quality** - Use text-based PDFs (not scanned images)
3. **Scoring** - Adjust thresholds based on position
4. **Keywords** - Use exact technology names
5. **Testing** - Test with 1 resume first

### Optimization:

- If rejecting too many: **Lower** SCORE_ACCEPT_THRESHOLD to 0.65
- If accepting too many: **Raise** SCORE_ACCEPT_THRESHOLD to 0.75
- Use exact terminology from successful previous hires
- Review "HOLD" candidates regularly

---

## 🔒 Security Best Practices

### Always:
- ✅ Keep `.env` and `oauth_credentials.json` secret
- ✅ Use App Passwords (not main Gmail password)
- ✅ Delete `token.pickle` when sharing code
- ✅ Add these files to `.gitignore` (already configured)
- ✅ Never commit secret files to version control
- ✅ Rotate credentials periodically
- ✅ Use OAuth2 (more secure than service accounts)

### OAuth2 Best Practices:
- ✅ Keep consent screen in "Testing" mode during development
- ✅ Add only your email as test user initially
- ✅ Request minimal scopes (calendar, email only)
- ✅ Delete and regenerate credentials if leaked
- ✅ Never hardcode credentials in code

### In Production:
- ✅ Move to "production" app status
- ✅ Complete OAuth verification with Google
- ✅ Use secure credential storage (AWS Secrets, etc.)
- ✅ Enable audit logging
- ✅ Implement access controls
- ✅ Follow GDPR and privacy regulations
- ✅ Handle candidate data responsibly

---

## 📦 What's Needed

### Minimum Setup
- Python 3.9+
- Gmail account
- Google account
- 5 resumes to test

### Recommended
- Virtual environment
- 2-4 hour setup time
- Basic computer literacy

### Total Investment
- Time: 1-2 hours setup, 5 min per run
- Cost: FREE (uses free tier APIs)

---

## ✨ What You Get

### Automated
- ✅ Resume screening
- ✅ Decision making
- ✅ Email sending
- ✅ Meeting scheduling

### Tracked
- ✅ All candidate data
- ✅ Scoring details
- ✅ Email logs
- ✅ Meeting links

### Visible
- ✅ Beautiful dashboard
- ✅ Analytics charts
- ✅ CSV exports
- ✅ Database queries

---

## 🚀 Quick Start Checklist

### Before Running:
- [ ] Gmail 2-Step Verification enabled
- [ ] Google Cloud project created
- [ ] OAuth2 scopes added (Calendar, Email)
- [ ] Test user email added to consent screen
- [ ] `oauth_credentials.json` downloaded and placed in folder
- [ ] `.env` file created with all variables
- [ ] Python packages installed (`pip install -r requirements.txt`)
- [ ] Validation passed (`python validate_setup.py`)

### First Run:
1. Add 1-2 test resumes to `resumes/` folder
2. Create `resumes/job_description.txt` with job requirements
3. Run: `python main_agent.py`
4. Watch as resumes are processed and meetings scheduled
5. Check acceptance emails sent to candidates
6. Verify Google Meet links in Google Calendar

### View Results:
1. Run: `streamlit run dashboard.py`
2. View candidate statuses, scores, and meeting links
3. Check email logs and analytics

### Iterate:
- Adjust scoring thresholds in `.env` if needed
- Add more resumes and run again
- Export data as CSV for analysis

---

## 📞 Getting Help

### If Something Goes Wrong:

1. **Read the error message** - It usually tells you exactly what's wrong
2. **Run validation**: `python validate_setup.py`
3. **Check your `.env` file** - Verify all variables are correct
4. **Review the Troubleshooting section** above
5. **Check folder structure** - Ensure all files are in right places
6. **Verify Google Cloud setup** - Confirm OAuth2 scopes and test user

### Common Issues Checklist:

- [ ] Is `.env` file created and has `GMAIL_PASSWORD` and `GOOGLE_OAUTH_CREDENTIALS=oauth_credentials.json`?
- [ ] Does `oauth_credentials.json` exist in `d:\HR_agent\`?
- [ ] Is your email added as test user in Google Cloud OAuth consent screen?
- [ ] Did you enable both Calendar API and Meet API?
- [ ] Are resume files in `resumes/` folder with correct extensions (.pdf, .docx)?
- [ ] Is `job_description.txt` created in `resumes/` folder?
- [ ] Did you activate the Python virtual environment?

### Still Stuck?

1. Delete `token.pickle` file and try again (forces new OAuth2 login)
2. Run: `python validate_setup.py --verbose` for detailed diagnostics
3. Check Python version: `python --version` (should be 3.9+)
4. Reinstall packages: `pip install -r requirements.txt --upgrade`

### Common Success Indicators:

✅ `python validate_setup.py` shows all green checks
✅ `python main_agent.py` processes at least 1 resume
✅ Emails received in candidate's inbox
✅ Google Meet link works
✅ Dashboard loads in browser

---

**🎉 You're All Set! Happy Hiring!**

*Last Updated: March 2026 | Version: 2.0*

