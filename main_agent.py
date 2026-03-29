import os
import hashlib
from datetime import datetime, timedelta

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
    """Production-ready AI HR Recruitment Agent"""

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
                print(f"❌ Job description file not found")
                return False

            with open(self.job_description_file, 'r', encoding='utf-8') as f:
                self.job_description = f.read()

            print(f"✅ JD loaded ({len(self.job_description)} chars)")
            return True

        except Exception as e:
            print(f"❌ Error loading JD: {e}")
            return False

    def load_job_description_from_folder(self):
        try:
            jd_path = os.path.join(self.job_folder, "jd.txt")

            if not os.path.exists(jd_path):
                print(f"❌ jd.txt missing in {self.job_folder}")
                return False

            with open(jd_path, 'r', encoding='utf-8') as f:
                self.job_description = f.read()

            print(f"✅ Job {self.job_id} JD loaded")
            return True

        except Exception as e:
            print(f"❌ Error loading JD: {e}")
            return False

    # =========================
    # FILE HANDLING
    # =========================
    def get_resume_files(self):
        folder = self.job_folder if self.job_folder else self.resume_folder

        return [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.endswith((".pdf", ".docx"))
        ]

    # =========================
    # HASHING (NEW)
    # =========================
    def get_file_hash(self, file_path):
        hasher = hashlib.md5()

        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)

        return hasher.hexdigest()

    # =========================
    # ENTRY POINT
    # =========================
    def process_job_resumes(self, user_id=None, hr_email=None):
        if not self.job_description:
            print("❌ JD not loaded")
            return

        files = self.get_resume_files()

        print(f"\n📂 Processing {len(files)} resumes (Job: {self.job_id})")

        for path in files:
            self.process_single_resume(path, user_id, hr_email)

    # =========================
    # CORE PROCESS
    # =========================
    def process_single_resume(self, resume_path, user_id=None, hr_email=None):
        try:
            filename = get_resume_filename(resume_path)

            print(f"\n{'='*60}")
            print(f"Processing: {filename}")
            print(f"{'='*60}")

            # HASH CHECK
            file_hash = self.get_file_hash(resume_path)

            if db.is_duplicate(file_hash):
                print(f"⚠️ Duplicate skipped: {filename}")
                return None

            # PARSE
            text = extract_resume_text(resume_path)
            if not text:
                return None

            info = extract_candidate_info(text)

            email = info.get('emails', ['unknown@email.com'])[0]
            phone = info.get('phones', [''])[0] if info.get('phones') else ''
            linkedin = info.get('linkedin', '')

            # NAME
            name_text = extract_candidate_name_from_text(text)
            name_file = extract_candidate_name_from_filename(filename)

            name = name_text if name_text and name_text != "Candidate" else name_file

            # EXTRA DATA
            skills = ", ".join(info.get("skills", []))
            experience = info.get("experience_years", 0)

            print(f"📧 {email}")
            print(f"🧠 Skills: {skills[:50]}")

            # MATCHING
            score = match_resume_to_job(text, self.job_description)
            report = generate_match_report(text, self.job_description, score)

            print(f"📊 Score: {report['score_percentage']}")

            # DECISION
            return self.make_hiring_decision(
                score,
                name,
                email,
                phone,
                linkedin,
                filename,
                file_hash,
                skills,
                experience,
                report,
                user_id,
                hr_email
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    # =========================
    # DECISION ENGINE
    # =========================
    def make_hiring_decision(
        self,
        score,
        name,
        email,
        phone,
        linkedin,
        resume_file,
        file_hash,
        skills,
        experience,
        report,
        user_id,
        hr_email=None
    ):

        candidate_id = db.add_candidate(
            job_id=self.job_id,
            name=name,
            email=email,
            phone=phone,
            resume_file=resume_file,
            file_hash=file_hash,
            match_score=score,
            summary=report.get('reason', ''),
            skills=skills,
            experience=experience,
            linkedin=linkedin,
            user_id=user_id
        )

        decision = {
            "candidate_id": candidate_id,
            "candidate_name": name,
            "candidate_email": email,
            "score": score
        }

        # =========================
        # DECISION LOGIC (UNCHANGED)
        # =========================
        if score >= SCORE_ACCEPT_THRESHOLD:
            decision["action"] = "ACCEPT"
            decision["reason"] = f"Strong match ({score*100:.1f}%)"

            db.update_candidate_status(candidate_id, "ACCEPTED", score)
            db.log_decision(user_id, candidate_id, "ACCEPT", decision["reason"])

            meeting = scheduler.schedule_interview(
                name,
                email,
                "Job Role",
                datetime.now() + timedelta(days=1),
                candidate_id,
                user_id=user_id,
                hr_email=hr_email
            )

            email_sender.send_acceptance_email(
                email,
                name,
                "Job Role",
                meeting_link=meeting.get("link") if meeting else None,
                meeting_time=meeting.get("time") if meeting else None
            )

        elif score >= SCORE_HOLD_THRESHOLD:
            decision["action"] = "HOLD"
            decision["reason"] = "Needs review"

            db.update_candidate_status(candidate_id, "UNDER_REVIEW", score)
            db.log_decision(user_id, candidate_id, "HOLD", decision["reason"])

        else:
            decision["action"] = "REJECT"
            decision["reason"] = "Low match"

            db.update_candidate_status(candidate_id, "REJECTED", score)
            db.log_decision(user_id,candidate_id, "REJECT", decision["reason"])

            email_sender.send_rejection_email(email, name, "Job Role")

        print(f"🎯 {decision['action']}")

        return decision


# =========================
# CLI SUPPORT
# =========================
if __name__ == "__main__":
    if not validate_config():
        exit()

    agent = HRRecruitmentAgent()
    agent.process_job_resumes()