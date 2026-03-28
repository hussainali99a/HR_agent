import os
from datetime import datetime, timedelta
from pathlib import Path

from config import (
    validate_config,
    RESUME_FOLDER,
    JOB_DESCRIPTION_FILE,
    SCORE_ACCEPT_THRESHOLD,
    SCORE_HOLD_THRESHOLD
)

from resume_parser import (
    extract_resume_text,
    extract_candidate_info,
    get_resume_filename,
    extract_candidate_name_from_filename,
    extract_candidate_name_from_text
)

from candidate_matcher import match_resume_to_job, generate_match_report
from email_sender import email_sender
from meet_scheduler import scheduler
from database import db


class HRRecruitmentAgent:
    """Main AI HR Recruitment Agent (Multi-JD Enabled)"""

    def __init__(self, job_id=None, job_folder=None):
        self.job_id = job_id
        self.job_folder = job_folder

        self.job_description = ""

        if job_folder:
            self.load_job_description_from_folder()
        else:
            self.resume_folder = RESUME_FOLDER
            self.job_description_file = JOB_DESCRIPTION_FILE
            self.load_job_description()

    # =========================
    # LOADERS
    # =========================
    def load_job_description(self):
        try:
            if not os.path.exists(self.job_description_file):
                print(f"❌ Job description file not found: {self.job_description_file}")
                return False

            with open(self.job_description_file, 'r', encoding='utf-8') as f:
                self.job_description = f.read()

            print(f"✅ Job description loaded ({len(self.job_description)} characters)")
            return True

        except Exception as e:
            print(f"❌ Error loading job description: {e}")
            return False

    def load_job_description_from_folder(self):
        try:
            jd_path = os.path.join(self.job_folder, "jd.txt")

            if not os.path.exists(jd_path):
                print(f"❌ jd.txt not found in {self.job_folder}")
                return False

            with open(jd_path, 'r', encoding='utf-8') as f:
                self.job_description = f.read()

            print(f"✅ Job {self.job_id} JD loaded ({len(self.job_description)} chars)")
            return True

        except Exception as e:
            print(f"❌ Error loading JD: {e}")
            return False

    # =========================
    # FILE HANDLING
    # =========================
    def get_resume_files(self):
        if self.job_folder:
            return [
                os.path.join(self.job_folder, f)
                for f in os.listdir(self.job_folder)
                if f.endswith((".pdf", ".docx"))
            ]
        else:
            return [
                os.path.join(self.resume_folder, f)
                for f in os.listdir(self.resume_folder)
                if f.endswith((".pdf", ".docx"))
            ]

    # =========================
    # DASHBOARD ENTRY
    # =========================
    def process_job_resumes(self):
        if not self.job_description:
            print("❌ Job description not loaded")
            return

        resume_files = self.get_resume_files()

        print(f"\n📂 Found {len(resume_files)} resumes for Job {self.job_id}")

        for resume_path in resume_files:
            self.process_single_resume(resume_path)

    # =========================
    # CORE PROCESSING
    # =========================
    def process_single_resume(self, resume_path, print_format="detailed"):
        try:
            filename = get_resume_filename(resume_path)

            print(f"\n{'='*60}")
            print(f"Processing: {filename}")
            print(f"{'='*60}")

            resume_text = extract_resume_text(resume_path)
            if not resume_text:
                return None

            candidate_info = extract_candidate_info(resume_text)
            candidate_email = candidate_info.get('emails', ['unknown@email.com'])[0]

            name_from_text = extract_candidate_name_from_text(resume_text)
            name_from_file = extract_candidate_name_from_filename(filename)

            if name_from_text and name_from_text != "Candidate":
                candidate_name = name_from_text
            else:
                candidate_name = name_from_file

            print(f"📧 Email: {candidate_email}")

            # MATCHING
            match_score = match_resume_to_job(resume_text, self.job_description)
            report = generate_match_report(resume_text, self.job_description, match_score)

            print(f"\n📊 MATCH ANALYSIS:")
            print(f"   Score: {report['score_percentage']}")
            print(f"   Status: {report['status']}")
            print(f"   Reason: {report['reason']}")

            # DECISION FLOW (UNCHANGED)
            decision = self.make_hiring_decision(
                match_score,
                candidate_name,
                candidate_email,
                filename,
                report,
                candidate_info
            )

            print(f"\n🎯 DECISION: {decision['action']}")
            print(f"   Reason: {decision['reason']}")

            return decision

        except Exception as e:
            print(f"❌ Error processing resume: {e}")
            return None

    # =========================
    # 🔥 ORIGINAL DECISION LOGIC (PRESERVED)
    # =========================
    def make_hiring_decision(self, score, candidate_name, candidate_email,
                            resume_file, report, candidate_info):

        candidate_id = db.add_candidate(
            name=candidate_name,
            email=candidate_email,
            phone=candidate_info.get('phones', [''])[0] if candidate_info.get('phones') else '',
            resume_file=resume_file,
            match_score=score,
            summary=report.get('reason', ''),
            job_id=self.job_id  # 🔥 ONLY CHANGE
        )

        decision = {
            'candidate_id': candidate_id,
            'candidate_name': candidate_name,
            'candidate_email': candidate_email,
            'score': score,
            'file': resume_file
        }

        if score >= SCORE_ACCEPT_THRESHOLD:
            decision['action'] = 'ACCEPT'
            decision['reason'] = f"Strong match ({score*100:.1f}%)"

            db.update_candidate_status(candidate_id, "ACCEPTED", score)
            db.log_decision(candidate_id, "ACCEPT", decision['reason'])

            # EMAIL + MEETING (UNCHANGED)
            meeting = scheduler.schedule_interview(
                candidate_name,
                candidate_email,
                "Job Role",
                datetime.now() + timedelta(days=1),
                candidate_id
            )

            email_sender.send_acceptance_email(
                candidate_email,
                candidate_name,
                "Job Role",
                meeting_link=meeting.get("link") if meeting else None,
                meeting_time=meeting.get("time") if meeting else None
            )

        elif score >= SCORE_HOLD_THRESHOLD:
            decision['action'] = 'HOLD'
            decision['reason'] = "Needs review"

            db.update_candidate_status(candidate_id, "UNDER_REVIEW", score)
            db.log_decision(candidate_id, "HOLD", decision['reason'])

        else:
            decision['action'] = 'REJECT'
            decision['reason'] = "Low match"

            db.update_candidate_status(candidate_id, "REJECTED", score)
            db.log_decision(candidate_id, "REJECT", decision['reason'])

            email_sender.send_rejection_email(candidate_email, candidate_name, "Job Role")

        return decision


# =========================
# CLI SUPPORT (UNCHANGED)
# =========================
if __name__ == "__main__":
    if not validate_config():
        exit()

    agent = HRRecruitmentAgent()
    agent.process_job_resumes()