# 🤖 AI HR Recruitment Agent - Complete Documentation

An intelligent, fully-automated recruitment system that evaluates resumes, schedules interviews, and sends professional emails to candidates using AI matching.

**Total Setup Time: 60-90 minutes (first time only)**

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

This AI-powered recruitment agent automates the entire hiring process:

1. **📥 Receives Applications** - Candidates submit resumes (PDF/DOCX)
2. **🤖 Analyzes Resumes** - AI matches resume to job requirements
3. **🎯 Makes Decisions** - Auto-accepts, rejects, or flags for review
4. **📧 Sends Emails** - Professional accept/reject notifications
5. **📅 Schedules Meetings** - Creates Google Meet links automatically
6. **📊 Tracks Everything** - Database and dashboard for insights

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
- **Python 3.9+** (Download from python.org)
- **Gmail Account** (with 2-Step Verification enabled)
- **Google Account** (for Calendar/Meet)
- **Candidate Resume Files** (PDF or DOCX format)

### Get These First:
1. Gmail: yourname@gmail.com
2. App Password (16 chars) from Gmail security settings
3. Google Cloud credentials.json file
4. Job description in text format

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

### ✅ STEP 2: Google Calendar Setup (10 minutes)

#### Go to Google Cloud Console:
1. Visit: https://console.cloud.google.com
2. Click project selector at the top
3. Click **"NEW PROJECT"**
4. Name it: `HR_Agent`
5. Click **CREATE**

#### Enable Calendar API:
1. Click **"ENABLE APIS AND SERVICES"** (top center)
2. Search for: `Google Calendar API`
3. Click it → Click **ENABLE**

#### Create Service Account:
1. Left menu → **Credentials**
2. **CREATE CREDENTIALS** → **Service Account**
3. Fill in:
   - **Name**: `hr-agent-user`
   - **Description**: `HR Agent for scheduling`
4. Click **CREATE AND CONTINUE**
5. Click through any remaining screens

#### Download JSON Key:
1. Go to **Credentials** page
2. Find your service account (email like: `xxx@xxx.iam.gserviceaccount.com`)
3. Click on it → **KEYS** tab
4. **ADD KEY** → **Create new key** → **JSON**
5. Click **CREATE**
6. File downloads - **RENAME to `credentials.json`**
7. **MOVE to `d:\HR_agent\` folder**

#### Set Calendar Permissions:
1. Visit: https://calendar.google.com
2. Settings → Add your service account email as calendar
3. Give it **Edit** permissions

---

### ✅ STEP 3: Create Configuration File (2 minutes)

1. Open Notepad
2. Copy this template (replace YOUR info):

```env
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_PASSWORD=your_16_char_app_password_here

GOOGLE_CREDENTIALS_FILE=credentials.json

OPENAI_API_KEY=sk_your_key_here

DATABASE_FILE=candidates.db
RESUME_FOLDER=resumes
JOB_DESCRIPTION_FILE=resumes/job_description.txt

INTERVIEW_DURATION_MINUTES=30
INTERVIEW_TIMEZONE=Asia/Kolkata

SCORE_ACCEPT_THRESHOLD=0.70
SCORE_HOLD_THRESHOLD=0.50
```

3. **Save as `.env`** in `d:\HR_agent\` folder
   - **IMPORTANT**: Save as "All Files" type (no .txt extension!)
   - File → Save As
   - Filename: `.env`
   - File type: All Files

**⚠️ SECRET FILE** - Never share or commit this!

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

Your folder must look like this:

```
d:\HR_agent\
├── .env                          ← Your config (SECRET!)
├── credentials.json              ← Google key (SECRET!)
├── requirements.txt
├── main_agent.py                 ← MAIN PROGRAM
├── dashboard.py                  ← View results
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
    ├── job_description.txt       ← Your job posting
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
✅ Google Calendar service initialized
✅ Job description loaded (3441 characters)

============================================================
🤖 HR RECRUITMENT AGENT STARTING
============================================================

📂 Found 2 resume(s) to process

============================================================
Processing: John_Doe.pdf
============================================================
✅ Resume parsed: John_Doe.pdf (5234 characters)
📧 Email: john@email.com

📊 MATCH ANALYSIS:
   Score: 78.5%
   Status: ACCEPT
   Reason: Strong match - 5+ years experience, Django expert

🎯 DECISION: ACCEPT
   Reason: Strong match (78.5%) - Qualifications align well

✅ Acceptance email sent to john@email.com
✅ Interview scheduled for John Doe
   Time: 2026-03-17T10:00:00
   Link: https://meet.google.com/abc-defg-hij

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

**Cause:** Virtual environment not activated

**Fix:**
```powershell
env-hr-agent\Scripts\activate
pip install -r requirements.txt
```

---

### Issue: "GMAIL_ADDRESS not set in .env"

**Cause:** `.env` file missing or empty

**Fix:**
1. Check `.env` exists in `d:\HR_agent\`
2. Check it has content
3. Recreate if necessary (see Step 3 above)

---

### Issue: "Credentials not found: credentials.json"

**Cause:** Google JSON key missing or wrong location

**Fix:**
1. Download from Google Cloud Console
2. Rename EXACTLY to: `credentials.json`
3. Place in `d:\HR_agent\` (not subfolder)
4. Check it's a valid JSON file

---

### Issue: "No resume files found"

**Cause:** Files in wrong location or format

**Fix:**
1. Check files in `resumes/` folder
2. Check extensions: `.pdf`, `.docx`, or `.doc`
3. Make sure names don't have weird characters
4. No `.lnk` shortcuts, only actual files

---

### Issue: "No text extracted from PDF"

**Cause:** PDF is scanned image, not text-based

**Fix:**
1. Use online tool to convert PDF (ilovepdf.com)
2. Or export PDF again from original document
3. Or convert to DOCX format instead

---

### Issue: "Email credential error"

**Cause:** App password wrong or 2-Step not enabled

**Fix:**
1. Check 2-Step Verification is ON
2. Check app password is exactly right (16 chars with spaces)
3. Make sure it's the app password, not regular password
4. Generate new app password if needed

---

### Issue: "Authentication failed"

**Cause:** Gmail 2-Step not enabled

**Fix:**
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Enable it (need your phone)
4. Get new app password

---

### Issue: "Google Calendar error"

**Cause:** Service account not set up correctly

**Fix:**
1. Check service account created in Google Cloud
2. Check service account email is added to Google Calendar
3. Verify Edit permissions set
4. Check credentials.json is valid

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
| `main_agent.py` | Main program - processes resumes and makes decisions |
| `dashboard.py` | Streamlit dashboard - view and analyze results |
| `validate_setup.py` | Validation script - checks configuration |
| `requirements.txt` | Python package dependencies |
| `config.py` | Configuration management |
| `database.py` | SQLite database operations |

### Processing Modules

| File | Purpose |
|------|---------|
| `resume_parser.py` | Extract text from PDF/DOCX files |
| `candidate_matcher.py` | AI scoring - match resume to job |
| `email_sender.py` | Gmail - send emails to candidates |
| `meet_scheduler.py` | Google Calendar - schedule interviews |

### Configuration (Keep Secret!)

| File | Purpose |
|------|---------|
| `.env` | Your credentials (Gmail, Google, settings) |
| `credentials.json` | Google Calendar service account JSON |

### Data Files (Created Automatically)

| File | Purpose |
|------|---------|
| `candidates.db` | SQLite database with all candidate data |
| `candidates_export.csv` | CSV export of candidates |

---

## 🔑 Environment Variables Reference

```env
# Gmail (For sending emails)
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_PASSWORD=your_16_character_app_password_here

# Google Calendar (For scheduling meetings)
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=primary

# OpenAI (Optional, for future features)
OPENAI_API_KEY=sk_your_key_here

# Database (Where data is stored)
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
- ✅ Keep `.env` and `credentials.json` secret
- ✅ Use App Passwords (not main Gmail password)
- ✅ Add these files to `.gitignore`
- ✅ Never share or commit these files
- ✅ Rotate credentials periodically

### In Production:
- ✅ Use environment variables
- ✅ Implement access controls
- ✅ Enable audit logging
- ✅ Follow GDPR/privacy laws
- ✅ Respect candidate data privacy

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

## 🚀 Next Steps

1. ✅ Follow **Complete Setup Guide** above (30 min)
2. ✅ Run `python validate_setup.py` (5 min)
3. ✅ Create `job_description.txt` (10 min)
4. ✅ Add 1-2 test PDFs (2 min)
5. ✅ Run `python main_agent.py` (5 min)
6. ✅ View `streamlit run dashboard.py` (5 min)
7. ✅ Customize and deploy (ongoing)

---

## 📞 Support

### If Something Goes Wrong:

1. Read the **Troubleshooting** section above
2. Run `python validate_setup.py`
3. Check `.env` file content
4. Review error messages carefully
5. Check folder structure is correct

### Common Success Indicators:

✅ `python validate_setup.py` shows all green checks
✅ `python main_agent.py` processes at least 1 resume
✅ Emails received in candidate's inbox
✅ Google Meet link works
✅ Dashboard loads in browser

---

**🎉 You're All Set! Happy Hiring!**

*Last Updated: March 2026 | Version: 2.0*

