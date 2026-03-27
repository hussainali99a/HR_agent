"""
Email Sender Module
Sends acceptance, rejection, and interview scheduling emails to candidates
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import GMAIL_ADDRESS, GMAIL_PASSWORD, EMAIL_SIGNATURE
from database import db

class EmailSender:
    """Handles all email communications"""
    
    def __init__(self):
        self.sender = GMAIL_ADDRESS
        self.password = GMAIL_PASSWORD
    
    def validate_credentials(self):
        """Test email credentials"""
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(self.sender, self.password)
            server.quit()
            print("✅ Email credentials validated successfully!")
            return True
        except Exception as e:
            print(f"❌ Email credential error: {e}")
            print("⚠️  Check your .env file - GMAIL_ADDRESS and GMAIL_PASSWORD must be correct")
            return False
    
    def send_acceptance_email(self, candidate_email, candidate_name, job_title, meeting_link=None, meeting_time=None, meeting_passcode=None):
        """Send acceptance email to candidate with meeting details"""
        try:
            subject = f"Great News! Your Application for {job_title} has been Accepted 🎉"
            
            body = f"""
Dear {candidate_name},

Congratulations! We are pleased to inform you that your application for the position of {job_title} has been shortlisted.

Your qualifications and experience align well with our requirements. We would like to move forward with the next step of our recruitment process.

"""
            
            if meeting_link and meeting_time:
                passcode_text = f"Passcode: {meeting_passcode}\n" if meeting_passcode else ""
                body += f"""
📅 INTERVIEW DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date & Time: {meeting_time}
Interview Link: {meeting_link}
{passcode_text}Type: Google Meet (Video Call)
Duration: 30 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 BEFORE THE INTERVIEW:
✓ Join 5 minutes early
✓ Test your camera and microphone
✓ Be in a quiet environment
✓ Have a good internet connection
✓ Keep your resume/portfolio ready

❓ If you have any questions or need to reschedule, please reply to this email or contact HR.

"""
            
            body += f"""
Best regards,

{EMAIL_SIGNATURE}
"""
            
            self.send_email(candidate_email, subject, message=body, is_html=False)
            print(f"✅ Acceptance email sent to {candidate_email}")
            
        except Exception as e:
            print(f"❌ Error sending acceptance email: {e}")
    
    def send_rejection_email(self, candidate_email, candidate_name, job_title):
        """Send rejection email to candidate"""
        try:
            subject = f"Application Status for {job_title}"
            
            body = f"""
Dear {candidate_name},

Thank you for your interest in the {job_title} position at our organization.

After careful consideration of your profile and qualifications, we regret to inform you that we have decided to move forward with other candidates whose skills more closely match our current requirements.

This decision was not easy, and we appreciate the time you invested in applying. We encourage you to apply for future positions that may be a better fit for your profile.

We wish you the very best in your career!

{EMAIL_SIGNATURE}
"""
            
            self.send_email(candidate_email, subject, body, is_html=False)
            print(f"✅ Rejection email sent to {candidate_email}")
            
        except Exception as e:
            print(f"❌ Error sending rejection email: {e}")
    
    def send_hold_email(self, candidate_email, candidate_name, job_title):
        """Send 'under review' email to candidate"""
        try:
            subject = f"Application Under Review for {job_title} ⏳"
            
            body = f"""
Dear {candidate_name},

Thank you for applying for the {job_title} position!

We have received your application and it is currently under review by our recruitment team. Your profile has shown promise, and we are carefully evaluating all candidates.

We will get back to you within the next 3-5 business days with an update.

{EMAIL_SIGNATURE}
"""
            
            self.send_email(candidate_email, subject, body, is_html=False)
            print(f"✅ Hold email sent to {candidate_email}")
            
        except Exception as e:
            print(f"❌ Error sending hold email: {e}")
    
    def send_interview_reminder(self, candidate_email, candidate_name, meeting_time, meeting_link):
        """Send interview reminder email"""
        try:
            subject = f"Interview Reminder - Tomorrow at {meeting_time} 📝"
            
            body = f"""
Dear {candidate_name},

This is a friendly reminder about your upcoming interview with us.

🗓️ Interview Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Time: {meeting_time}
Link: {meeting_link}
Duration: 30 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please make sure to:
✓ Join 5 minutes early
✓ Test your camera and microphone
✓ Be in a quiet environment
✓ Have good internet connection

Looking forward to speaking with you!

{EMAIL_SIGNATURE}
"""
            
            self.send_email(candidate_email, subject, body, is_html=False)
            print(f"✅ Reminder email sent to {candidate_email}")
            
        except Exception as e:
            print(f"❌ Error sending reminder email: {e}")
    
    def send_email(self, receiver, subject, message, is_html=False):
        """Generic email sending function"""
        try:
            if not self.sender or not self.password:
                print("❌ Email credentials not configured. Check your .env file")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = receiver
            
            # Add body
            msg.attach(MIMEText(message, 'html' if is_html else 'plain'))
            
            # Send email
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Error in send_email: {e}")
            return False

# Global email sender instance
email_sender = EmailSender()

if __name__ == "__main__":
    # Test email sending
    print("Testing email sender...")
    
    # Validate credentials
    if email_sender.validate_credentials():
        print("✅ Email system is ready!")
    else:
        print("❌ Email system configuration needed")