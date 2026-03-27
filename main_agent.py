"""
Main HR Recruitment Agent
Orchestrates the entire recruitment process
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Import all modules
from config import (validate_config, RESUME_FOLDER, JOB_DESCRIPTION_FILE,
                    SCORE_ACCEPT_THRESHOLD, SCORE_HOLD_THRESHOLD)
from resume_parser import extract_resume_text, extract_candidate_info, get_resume_filename, extract_candidate_name_from_filename, extract_candidate_name_from_text
from candidate_matcher import match_resume_to_job, generate_match_report
from email_sender import email_sender
from meet_scheduler import scheduler
from database import db

class HRRecruitmentAgent:
    """Main AI HR Recruitment Agent"""
    
    def __init__(self):
        self.resume_folder = RESUME_FOLDER
        self.job_description_file = JOB_DESCRIPTION_FILE
        self.job_description = ""
        self.load_job_description()
    
    def load_job_description(self):
        """Load job description from file"""
        try:
            if not os.path.exists(self.job_description_file):
                print(f"❌ Job description file not found: {self.job_description_file}")
                print("📌 Please create 'resumes/job_description.txt' with the job details")
                return False
            
            with open(self.job_description_file, 'r', encoding='utf-8') as f:
                self.job_description = f.read()
            
            print(f"✅ Job description loaded ({len(self.job_description)} characters)")
            return True
        
        except Exception as e:
            print(f"❌ Error loading job description: {e}")
            return False
    
    def process_single_resume(self, resume_path, print_format="detailed"):
        """
        Process a single resume and make hiring decision
        
        Args:
            resume_path: Path to resume PDF
            print_format: 'detailed' or 'summary'
        
        Returns:
            Dictionary with processing results
        """
        try:
            if not self.job_description:
                print("❌ Job description not loaded. Cannot process resumes.")
                return None
            
            filename = get_resume_filename(resume_path)
            print(f"\n{'='*60}")
            print(f"Processing: {filename}")
            print(f"{'='*60}")
            
            # Extract resume text
            resume_text = extract_resume_text(resume_path)
            if not resume_text:
                print(f"❌ Could not extract text from {filename}")
                return None
            
            # Extract candidate info
            candidate_info = extract_candidate_info(resume_text)
            candidate_email = candidate_info.get('emails', ['unknown@email.com'])[0]
            
            # Extract name from text and filename
            name_from_text = extract_candidate_name_from_text(resume_text)
            name_from_file = extract_candidate_name_from_filename(filename)
            
            # Smart name selection:
            # - Prefer name from text IF it has more words than filename
            # - Otherwise use filename (usually more reliable)
            # - Fallback to text if filename is just "Candidate"
            if name_from_text and name_from_text != "Candidate":
                text_word_count = len(name_from_text.split())
                file_word_count = len(name_from_file.split())
                candidate_name = name_from_text if text_word_count > file_word_count else name_from_file
            else:
                candidate_name = name_from_file if name_from_file != "Candidate" else name_from_text or "Candidate"
            
            print(f"📧 Email: {candidate_email}")
            print(f"📝 Resume size: {len(resume_text)} characters")
            
            # Match resume to job
            match_score = match_resume_to_job(resume_text, self.job_description)
            report = generate_match_report(resume_text, self.job_description, match_score)
            
            # Print matching details
            print(f"\n📊 MATCH ANALYSIS:")
            print(f"   Score: {report['score_percentage']}")
            print(f"   Status: {report['status']}")
            print(f"   Reason: {report['reason']}")
            
            if report.get('matching_keywords'):
                print(f"   ✓ Matched Keywords: {', '.join(report['matching_keywords'][:5])}")
            
            if report.get('missing_keywords'):
                print(f"   ✗ Missing Keywords: {', '.join(report['missing_keywords'][:3])}")
            
            # Make decision
            decision = self.make_hiring_decision(
                match_score, candidate_name, candidate_email, 
                filename, report, candidate_info
            )
            
            print(f"\n🎯 DECISION: {decision['action']}")
            print(f"   Reason: {decision['reason']}")
            
            if print_format == "detailed":
                print(f"\n📋 CANDIDATE INFO:")
                print(f"   Skills: {', '.join(candidate_info.get('skills', [])[:5])}")
                print(f"   Experience: {candidate_info.get('experience_years', 0)} years")
                print(f"   LinkedIn: {candidate_info.get('linkedin', 'Not provided')}")
            
            return decision
        
        except IndexError as e:
            print(f"❌ Index error processing resume: {e}")
            print(f"   This usually means data extraction failed. Try a different resume format.")
            return None
        except Exception as e:
            print(f"❌ Error processing resume: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def make_hiring_decision(self, score, candidate_name, candidate_email,
                            resume_file, report, candidate_info):
        """
        Make a hiring decision based on match score
        
        Args:
            score: Match score (0-1)
            candidate_name: Candidate name
            candidate_email: Candidate email
            resume_file: Resume filename
            report: Matching report
            candidate_info: Extracted candidate info
        
        Returns:
            Decision dictionary
        """
        try:
            # Add candidate to database
            candidate_id = db.add_candidate(
                name=candidate_name,
                email=candidate_email,
                phone=candidate_info.get('phones', [''])[0] if candidate_info.get('phones') else '',
                resume_file=resume_file,
                match_score=score,
                summary=report.get('reason', '')
            )
            
            decision = {
                'candidate_id': candidate_id,
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'score': score,
                'file': resume_file
            }
            
            # Decision logic based on score
            if score >= SCORE_ACCEPT_THRESHOLD:
                decision['action'] = 'ACCEPT'
                decision['reason'] = f"Strong match ({score*100:.1f}%) - Qualifications align well"
                
                # Update database
                db.update_candidate_status(candidate_id, "ACCEPTED", score)
                db.log_decision(candidate_id, "ACCEPT", decision['reason'])
                
                # Setup variables
                job_title = "our open position"  # Will be enhanced later
                meeting_link = None
                meeting_time = None
                meeting_passcode = None
                meeting_scheduled = False
                
                # Attempt to schedule meeting FIRST
                meeting_result = self.schedule_interview_for_candidate(
                    candidate_id, candidate_name, candidate_email
                )
                
                if meeting_result:
                    meeting_scheduled = True
                    meeting_link = meeting_result.get('meeting_link')
                    meeting_time = meeting_result.get('meeting_time')
                    meeting_passcode = meeting_result.get('meeting_passcode')
                    decision['meeting_scheduled'] = True
                    decision['meeting_link'] = meeting_link
                    decision['meeting_passcode'] = meeting_passcode
                    decision['meeting_event_id'] = meeting_result.get('event_id')
                else:
                    decision['meeting_scheduled'] = False
                
                # Send SINGLE acceptance email with or without meeting details
                email_sender.send_acceptance_email(
                    candidate_email, candidate_name, job_title,
                    meeting_link=meeting_link,
                    meeting_time=meeting_time,
                    meeting_passcode=meeting_passcode
                )
                
                # Log the email sent
                email_subject = f"Great News! Your Application for {job_title} has been Accepted 🎉"
                db.log_email(candidate_id, "ACCEPTANCE", email_subject, "SENT")
            
            elif score >= SCORE_HOLD_THRESHOLD:
                decision['action'] = 'HOLD'
                decision['reason'] = f"Moderate match ({score*100:.1f}%) - Requires manual review"
                
                db.update_candidate_status(candidate_id, "UNDER_REVIEW", score)
                db.log_decision(candidate_id, "HOLD", decision['reason'])
                
                # Send hold email
                email_sender.send_hold_email(candidate_email, candidate_name, "our position")
                
                # Log the email
                db.log_email(candidate_id, "HOLD", f"Application Under Review for our position ⏳", "SENT")
            
            else:
                decision['action'] = 'REJECT'
                decision['reason'] = f"Insufficient match ({score*100:.1f}%) - Experience/skills don't align"
                
                db.update_candidate_status(candidate_id, "REJECTED", score)
                db.log_decision(candidate_id, "REJECT", decision['reason'])
                
                # Send rejection email
                email_sender.send_rejection_email(candidate_email, candidate_name, "our position")
                
                # Log the email
                db.log_email(candidate_id, "REJECTION", f"Application Status for our position", "SENT")
            
            return decision
        
        except Exception as e:
            print(f"❌ Error in decision making: {e}")
            return {'action': 'ERROR', 'reason': str(e)}
    
    def schedule_interview_for_candidate(self, candidate_id, candidate_name, candidate_email):
        """Try to schedule an interview for accepted candidate with fallback options"""
        try:
            # Preferred time: next working day at 10 AM
            next_interview = datetime.now() + timedelta(days=1)
            
            # Make sure it's a working day (Mon-Fri)
            while next_interview.weekday() > 4:  # 5=Saturday, 6=Sunday
                next_interview += timedelta(days=1)
            
            next_interview = next_interview.replace(hour=10, minute=0, second=0)
            
            # Try to schedule at preferred time
            print(f"📅 Attempting to schedule interview for {candidate_name} on {next_interview}")
            
            result = scheduler.schedule_interview(
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title="our open position",
                interview_date_time=next_interview,
                candidate_id=candidate_id
            )
            
            if result:
                print(f"✅ Successfully scheduled meeting for {candidate_name}")
                return result
            
            # If primary time fails, try 2 PM instead
            print(f"⚠️  Could not schedule at 10 AM, trying 2 PM...")
            next_interview = next_interview.replace(hour=14, minute=0, second=0)
            
            result = scheduler.schedule_interview(
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title="our open position",
                interview_date_time=next_interview,
                candidate_id=candidate_id
            )
            
            if result:
                print(f"✅ Successfully scheduled meeting at 2 PM for {candidate_name}")
                return result
            
            # If both fail, log the issue but don't stop the process
            print(f"⚠️  Could not schedule automatic meeting for {candidate_name}")
            print(f"    Candidate will need to schedule manually or HR will follow up")
            return None
        
        except Exception as e:
            print(f"⚠️  Error in meeting scheduling: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_all_resumes(self):
        """
        Process all resumes in the resume folder
        Main entry point for the agent
        """
        print("\n" + "="*60)
        print("🤖 HR RECRUITMENT AGENT STARTING")
        print("="*60)
        
        # Validate configuration
        if not validate_config():
            print("\n❌ Configuration validation failed!")
            return False
        
        # Load job description
        if not self.load_job_description():
            print("\n❌ Cannot proceed without job description")
            return False
        
        # Check if resume folder exists
        if not os.path.exists(self.resume_folder):
            print(f"❌ Resume folder not found: {self.resume_folder}")
            return False
        
        # Get all resume files (PDF and DOCX)
        resume_files = [f for f in os.listdir(self.resume_folder) if f.endswith(('.pdf', '.docx', '.doc'))]
        
        if not resume_files:
            print(f"⚠️  No resume files found in {self.resume_folder} (looking for .pdf, .docx, or .doc)")
            return False
        
        print(f"\n📂 Found {len(resume_files)} resume(s) to process\n")
        
        # Process each resume
        results = []
        for resume_file in resume_files:
            resume_path = os.path.join(self.resume_folder, resume_file)
            result = self.process_single_resume(resume_path)
            
            if result:
                results.append(result)
        
        # Print summary
        self.print_summary(results)
        
        return True
    
    def print_summary(self, results):
        """Print summary of processing"""
        print("\n" + "="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        
        if not results:
            print("No results to summarize")
            return
        
        accepted = [r for r in results if r['action'] == 'ACCEPT']
        held = [r for r in results if r['action'] == 'HOLD']
        rejected = [r for r in results if r['action'] == 'REJECT']
        
        print(f"\n✅ ACCEPTED: {len(accepted)} candidates")
        for r in accepted:
            print(f"   - {r['candidate_name']} ({r['score']*100:.1f}%)")
        
        print(f"\n⏳ UNDER REVIEW: {len(held)} candidates")
        for r in held:
            print(f"   - {r['candidate_name']} ({r['score']*100:.1f}%)")
        
        print(f"\n❌ REJECTED: {len(rejected)} candidates")
        for r in rejected:
            print(f"   - {r['candidate_name']} ({r['score']*100:.1f}%)")
        
        print(f"\n Total Processed: {len(results)}")
        print("="*60)
        
        # Export to CSV
        db.export_to_csv("candidates_export.csv")

def main():
    """Main entry point"""
    try:
        agent = HRRecruitmentAgent()
        agent.process_all_resumes()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Agent interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
