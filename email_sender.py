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
    
    # Professional color scheme
    PRIMARY_COLOR = "#1F4788"      # Dark blue
    SUCCESS_COLOR = "#28a745"      # Green
    SECONDARY_COLOR = "#6c757d"    # Gray
    LIGHT_BG = "#f8f9fa"           # Light gray background
    BORDER_COLOR = "#dee2e6"       # Border gray
    
    def __init__(self):
        self.sender = GMAIL_ADDRESS
        self.password = GMAIL_PASSWORD
    
    
    def get_email_header(self):
        """Return professional email header HTML"""
        return f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff;">
            <tr>
                <td style="padding: 20px 0; background-color: {self.PRIMARY_COLOR}; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: 300;">
                        Recruitment Team
                    </h1>
                    <p style="color: #e8f0f8; margin: 5px 0 0 0; font-size: 14px;">HR Department</p>
                </td>
            </tr>
        </table>
        """
    
    def get_email_footer(self):
        """Return professional email footer HTML"""
        return f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: {self.LIGHT_BG}; margin-top: 30px;">
            <tr>
                <td style="padding: 25px; text-align: center; color: {self.SECONDARY_COLOR}; font-size: 12px; line-height: 1.8; font-family: 'Segoe UI', Arial, sans-serif;">
                    <p style="margin: 0 0 10px 0;">
                        <strong style="color: {self.PRIMARY_COLOR};">Recruitment Team</strong><br>
                        HR Department
                    </p>
                    <p style="margin: 10px 0; border-top: 1px solid {self.BORDER_COLOR}; padding-top: 10px;">
                        If you have any questions, please feel free to reach out to us.<br>
                        We're here to help!
                    </p>
                </td>
            </tr>
        </table>
        """
    
    def get_email_wrapper(self, content):
        """Wrap content with professional HTML structure"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                }}
                .email-wrapper {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border: 1px solid {self.BORDER_COLOR};
                    border-radius: 4px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .email-body {{
                    padding: 30px 25px;
                }}
                h2 {{
                    color: {self.PRIMARY_COLOR};
                    font-size: 20px;
                    margin-top: 0;
                    margin-bottom: 15px;
                }}
                .section-box {{
                    background-color: {self.LIGHT_BG};
                    border-left: 4px solid {self.PRIMARY_COLOR};
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 2px;
                }}
                .button {{
                    display: inline-block;
                    background-color: {self.PRIMARY_COLOR};
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: 600;
                    margin: 15px 0;
                }}
                .button:hover {{
                    background-color: #163458;
                }}
                .info-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    background-color: {self.LIGHT_BG};
                    border-radius: 4px;
                    overflow: hidden;
                }}
                .info-table td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid {self.BORDER_COLOR};
                }}
                .info-table tr:last-child td {{
                    border-bottom: none;
                }}
                .info-label {{
                    font-weight: 600;
                    color: {self.PRIMARY_COLOR};
                    width: 35%;
                }}
                .checkbox-item {{
                    padding: 8px 0;
                    margin-left: 20px;
                }}
                .success-badge {{
                    display: inline-block;
                    background-color: {self.SUCCESS_COLOR};
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                {self.get_email_header()}
                <div class="email-body">
                    {content}
                </div>
                {self.get_email_footer()}
            </div>
        </body>
        </html>
        """
    
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
            subject = f"Congratulations! Your Application for {job_title} Has Been Accepted"
            
            # Build the email content
            content = f"""
            <h2>Dear {candidate_name},</h2>
            
            <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                <strong style="color: {self.SUCCESS_COLOR}; font-size: 18px;">🎉 Congratulations!</strong>
            </p>
            
            <p>
                We are delighted to inform you that your application for the position of <strong>{job_title}</strong> 
                has been successfully shortlisted. Your qualifications and experience align excellently with our 
                requirements, and we are excited about the possibility of working with you.
            </p>
            
            <p>
                We would like to move forward by scheduling an interview to discuss this opportunity in greater detail.
            </p>
            """
            
            if meeting_link and meeting_time:
                passcode_html = f"<tr><td class='info-label'>Passcode:</td><td>{meeting_passcode}</td></tr>" if meeting_passcode else ""
                content += f"""
            <div class="section-box" style="border-left-color: {self.SUCCESS_COLOR}; background-color: #f0f9f4;">
                <p style="margin-top: 0; color: {self.PRIMARY_COLOR}; font-weight: 600; font-size: 14px;">📅 INTERVIEW DETAILS</p>
                <table class="info-table" style="background-color: #ffffff;">
                    <tr>
                        <td class="info-label">Date & Time:</td>
                        <td>{meeting_time}</td>
                    </tr>
                    <tr>
                        <td class="info-label">Platform:</td>
                        <td>Google Meet (Video Call)</td>
                    </tr>
                    <tr>
                        <td class="info-label">Duration:</td>
                        <td>30 minutes</td>
                    </tr>
                    <tr>
                        <td class="info-label">Meeting Link:</td>
                        <td><a href="{meeting_link}" style="color: {self.PRIMARY_COLOR}; text-decoration: none; font-weight: 600;">{meeting_link}</a></td>
                    </tr>
                    {passcode_html}
                </table>
            </div>
            
            <div class="section-box" style="border-left-color: {self.PRIMARY_COLOR};">
                <p style="margin-top: 0; color: {self.PRIMARY_COLOR}; font-weight: 600; font-size: 14px;">✓ INTERVIEW PREPARATION CHECKLIST</p>
                <div class="checkbox-item">✓ Join 5 minutes early</div>
                <div class="checkbox-item">✓ Test your camera and microphone</div>
                <div class="checkbox-item">✓ Ensure a quiet, professional environment</div>
                <div class="checkbox-item">✓ Verify your internet connection stability</div>
                <div class="checkbox-item">✓ Have your resume and portfolio ready</div>
                <div class="checkbox-item">✓ Keep pen and paper handy for notes</div>
            </div>
            
            <p style="margin-top: 20px; color: {self.SECONDARY_COLOR}; font-size: 14px;">
                <strong>Need to reschedule?</strong> If you cannot make this interview time, 
                please reply to this email as soon as possible so we can find an alternative time that works for you.
            </p>
            """
            else:
                content += """
            <p>
                We will soon send you the detailed interview schedule and meeting link. 
                Please keep an eye on your inbox for further communication.
            </p>
            """
            
            content += """
            <p style="margin-top: 30px; margin-bottom: 5px;">
                Looking forward to meeting you soon!
            </p>
            <p style="margin: 0;">
                Best regards,<br>
                <strong style="color: """ + self.PRIMARY_COLOR + """;">Recruitment Team</strong><br>
                HR Department
            </p>
            """
            
            html_content = self.get_email_wrapper(content)
            self.send_email(candidate_email, subject, html_content, is_html=True)
            print(f"✅ Acceptance email sent to {candidate_email}")
            
        except Exception as e:
            print(f"❌ Error sending acceptance email: {e}")
    
    
    def send_rejection_email(self, candidate_email, candidate_name, job_title):
        """Send rejection email to candidate"""
        try:
            subject = f"Your Application for {job_title} — Next Steps"
            
            content = f"""
            <h2>Dear {candidate_name},</h2>
            
            <p>
                Thank you for your interest in the <strong>{job_title}</strong> position at our organization. 
                We truly appreciate the time and effort you invested in your application and the interview process.
            </p>
            
            <p style="color: #666;">
                After a thorough review of all candidates, we have decided to move forward with applicants whose qualifications 
                more closely match our current requirements. This was not an easy decision, as we recognized the value in your profile.
            </p>
            
            <div class="section-box" style="border-left-color: {self.PRIMARY_COLOR};">
                <p style="margin-top: 0; color: {self.PRIMARY_COLOR}; font-weight: 600; font-size: 14px;">💡 WHAT'S NEXT?</p>
                <p style="margin-bottom: 10px;">
                    We encourage you to apply for future positions that align even better with your skills and experience. 
                    Your profile will be retained for a period of time, and we may contact you if a more suitable opportunity arises.
                </p>
            </div>
            
            <p>
                Please feel free to connect with us on LinkedIn or visit our careers page to explore other open positions. 
                We wish you the very best in your career journey!
            </p>
            
            <p style="margin-top: 30px; margin-bottom: 5px;">
                Best regards,<br>
                <strong style="color: """ + self.PRIMARY_COLOR + """;">Recruitment Team</strong><br>
                HR Department
            </p>
            """
            
            html_content = self.get_email_wrapper(content)
            self.send_email(candidate_email, subject, html_content, is_html=True)
            print(f"✅ Rejection email sent to {candidate_email}")
            
        except Exception as e:
            print(f"❌ Error sending rejection email: {e}")
    
    
    def send_hold_email(self, candidate_email, candidate_name, job_title):
        """Send 'under review' email to candidate"""
        try:
            subject = f"Your Application for {job_title} — Under Review"
            
            content = f"""
            <h2>Dear {candidate_name},</h2>
            
            <p>
                Thank you for applying for the <strong>{job_title}</strong> position! 
                We are excited to have received your application.
            </p>
            
            <div class="section-box" style="border-left-color: {self.PRIMARY_COLOR};">
                <p style="margin-top: 0; color: {self.PRIMARY_COLOR}; font-weight: 600; font-size: 14px;">⏳ APPLICATION STATUS</p>
                <p style="margin: 10px 0;">
                    Your profile is currently being reviewed by our recruitment team. Your qualifications show promise, 
                    and we are carefully evaluating all candidates to ensure we find the best match for our team.
                </p>
            </div>
            
            <table class="info-table">
                <tr>
                    <td class="info-label">Expected Timeline:</td>
                    <td>3-5 business days</td>
                </tr>
                <tr>
                    <td class="info-label">Next Update:</td>
                    <td>We'll follow up with you shortly</td>
                </tr>
            </table>
            
            <p style="color: {self.SECONDARY_COLOR}; font-size: 14px;">
                <strong>In the meantime:</strong> Keep an eye on your inbox for our updates. 
                If you have any questions, please feel free to reach out to us.
            </p>
            
            <p style="margin-top: 30px; margin-bottom: 5px;">
                Thank you for your patience!<br>
                <strong style="color: """ + self.PRIMARY_COLOR + """;">Recruitment Team</strong><br>
                HR Department
            </p>
            """
            
            html_content = self.get_email_wrapper(content)
            self.send_email(candidate_email, subject, html_content, is_html=True)
            print(f"✅ Hold email sent to {candidate_email}")
            
        except Exception as e:
            print(f"❌ Error sending hold email: {e}")
    
    
    def send_interview_reminder(self, candidate_email, candidate_name, meeting_time, meeting_link):
        """Send interview reminder email"""
        try:
            subject = f"Interview Reminder — {meeting_time}"
            
            content = f"""
            <h2>Dear {candidate_name},</h2>
            
            <p style="font-size: 16px; color: {self.PRIMARY_COLOR}; font-weight: 600;">
                📝 Interview Reminder
            </p>
            
            <p>
                This is a friendly reminder about your upcoming interview with us. We're looking forward to meeting you!
            </p>
            
            <div class="section-box" style="border-left-color: {self.PRIMARY_COLOR};">
                <p style="margin-top: 0; color: {self.PRIMARY_COLOR}; font-weight: 600; font-size: 14px;">🗓️ INTERVIEW DETAILS</p>
                <table class="info-table">
                    <tr>
                        <td class="info-label">Date & Time:</td>
                        <td><strong>{meeting_time}</strong></td>
                    </tr>
                    <tr>
                        <td class="info-label">Format:</td>
                        <td>Google Meet (Video Call)</td>
                    </tr>
                    <tr>
                        <td class="info-label">Duration:</td>
                        <td>30 minutes</td>
                    </tr>
                    <tr>
                        <td class="info-label">Meeting Link:</td>
                        <td><a href="{meeting_link}" style="color: {self.PRIMARY_COLOR}; text-decoration: none; font-weight: 600;;">{meeting_link}</a></td>
                    </tr>
                </table>
            </div>
            
            <div class="section-box" style="border-left-color: {self.SUCCESS_COLOR}; background-color: #f0f9f4;">
                <p style="margin-top: 0; color: {self.PRIMARY_COLOR}; font-weight: 600; font-size: 14px;">✓ QUICK CHECKLIST</p>
                <div class="checkbox-item">✓ Join 5 minutes before the scheduled time</div>
                <div class="checkbox-item">✓ Test your camera, microphone, and speakers</div>
                <div class="checkbox-item">✓ Find a quiet, professional location</div>
                <div class="checkbox-item">✓ Check your internet connection</div>
                <div class="checkbox-item">✓ Have your resume readily available</div>
                <div class="checkbox-item">✓ Wear professional attire</div>
            </div>
            
            <p style="color: {self.SECONDARY_COLOR}; font-size: 14px; margin-bottom: 10px;">
                <strong>Pro Tip:</strong> Consider having some water nearby and ensure good lighting in your space 
                for the best video call experience.
            </p>
            
            <p style="margin-top: 30px; margin-bottom: 5px;">
                We look forward to speaking with you!<br>
                <strong style="color: """ + self.PRIMARY_COLOR + """;">Recruitment Team</strong><br>
                HR Department
            </p>
            """
            
            html_content = self.get_email_wrapper(content)
            self.send_email(candidate_email, subject, html_content, is_html=True)
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
            
            # Add body with proper MIME type
            msg.attach(MIMEText(message, 'html' if is_html else 'plain', 'utf-8'))
            
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