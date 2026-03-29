"""
Meet Scheduler Module
Schedules real Google Meet interviews with proper calendar integration
"""

from googleapiclient.discovery import build
from datetime import timedelta
import uuid
import os
from google_auth import GoogleAuthHandler
from config import INTERVIEW_TIMEZONE, INTERVIEW_DURATION_MINUTES
from database import db

class MeetScheduler:
    """Handles real Google Meet scheduling"""
    
    def __init__(self):
        self.timezone = INTERVIEW_TIMEZONE
        self.duration = INTERVIEW_DURATION_MINUTES
        
        # Initialize OAuth2 auth
        try:
            auth_handler = GoogleAuthHandler()
            creds = auth_handler.get_credentials()
            
            # Initialize services
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            self.meet_service = build('meet', 'v2', credentials=creds)
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            
            print("✅ Google services initialized successfully")
            print("📅 Google Calendar API ready")
            print("🎥 Google Meet API ready")
            print("📧 Gmail API ready")
            
        except FileNotFoundError:
            print("❌ oauth_credentials.json not found!")
            print("   Please follow setup instructions in SETUP_GUIDE.md")
            self.calendar_service = None
            self.meet_service = None
            self.gmail_service = None
        except Exception as e:
            print(f"❌ Error initializing services: {e}")
            self.calendar_service = None
            self.meet_service = None
            self.gmail_service = None
    
    def create_google_meet_space(self):
        """
        Create a real Google Meet space
        Returns the actual meeting URI that Google generates
        """
        try:
            if not self.meet_service:
                print("❌ Google Meet service not available")
                return None
            
            # Create a new space
            request_body = {}
            response = self.meet_service.spaces().create(body=request_body).execute()
            
            meeting_uri = response.get('meetingUri', '')
            
            if meeting_uri:
                print(f"✅ Real Google Meet created: {meeting_uri}")
                return meeting_uri
            else:
                print("⚠️  No meeting URI returned")
                return None
                
        except Exception as e:
            print(f"⚠️  Could not create Meet space: {e}")
            print("   This is normal if Meet API has restrictions")
            return None
    
    def schedule_interview(self, candidate_name, candidate_email, job_title, 
                          interview_date_time, candidate_id=None, user_id=None, hr_email=None):
        """
        Schedule an interview with Google Meet
        
        Args:
            candidate_name: Name of candidate
            candidate_email: Email of candidate
            job_title: Position title
            interview_date_time: datetime object for interview start time
            candidate_id: Database candidate ID
        
        Returns:
            Dictionary with meeting details or None if failed
        """
        try:
            if not self.calendar_service:
                print("❌ Calendar service not available")
                return None
            
            # Validate input
            if not candidate_email or '@' not in candidate_email:
                print(f"❌ Invalid email: {candidate_email}")
                return None
            
            # Calculate end time
            interview_end = interview_date_time + timedelta(minutes=self.duration)
            
            # Try to create real Google Meet space
            meeting_uri = self.create_google_meet_space()
            
            # If Meet API not available, use calendar-generated Meet
            use_calendar_meet = meeting_uri is None
            
            # Create calendar event
            event_body = {
                'summary': f'Interview: {candidate_name} - {job_title}',
                'description': f'''HR Interview for {job_title}

CANDIDATE DETAILS:
Name: {candidate_name}
Email: {candidate_email}

MEETING INSTRUCTIONS:
• You will receive a Google Calendar invite
• Click the "Join with Google Meet" link in the calendar event
• No passcode needed
• Join 5 minutes early
• Test video/audio before interview starts

IMPORTANT:
✓ Use a quiet environment
✓ Have good internet connection
✓ Professional background
✓ Keep resume ready

Questions? Contact HR immediately.
''',
                'start': {
                    'dateTime': interview_date_time.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': interview_end.isoformat(),
                    'timeZone': self.timezone,
                },
                'attendees': [
                    {'email': candidate_email, 'responseStatus': 'needsAction'},
                    {'email': hr_email, 'responseStatus': 'needsAction'}
                ]
            }
            
            # Add Google Meet via Calendar if not created via Meet API
            if use_calendar_meet:
                event_body['conferenceData'] = {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            
            # Insert event
            insert_params = {
                'calendarId': 'primary',
                'body': event_body,
                'sendUpdates': 'all'
            }
            
            if use_calendar_meet:
                insert_params['conferenceDataVersion'] = 1
            
            created_event = self.calendar_service.events().insert(**insert_params).execute()
            
            # Extract meeting link from response
            meeting_link = meeting_uri
            if not meeting_link and 'conferenceData' in created_event:
                meeting_link = created_event['conferenceData'].get('entryPoints', [{}])[0].get('uri', '')
            
            meeting_time = created_event.get('start', {}).get('dateTime', '')
            event_id = created_event.get('id', '')
            calendar_link = created_event.get('htmlLink', '')
            
            print(f"✅ Interview scheduled for {candidate_name}")
            print(f"   Date/Time: {meeting_time}")
            print(f"   Calendar Event: {calendar_link}")
            if meeting_link:
                print(f"   Google Meet: {meeting_link}")
            
            # Log to database
            if candidate_id:
                db.schedule_interview(candidate_id, user_id, meeting_link, meeting_time)
            
            return {
                'meeting_link': meeting_link or calendar_link,
                'meeting_time': meeting_time,
                'event_id': event_id,
                'calendar_link': calendar_link
            }
        
        except Exception as e:
            print(f"❌ Error scheduling interview: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def reschedule_interview(self, event_id, new_date_time):
        """Reschedule an existing interview"""
        try:
            if not self.calendar_service:
                return None
            
            event = self.calendar_service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            new_end = new_date_time + timedelta(minutes=self.duration)
            
            event['start']['dateTime'] = new_date_time.isoformat()
            event['end']['dateTime'] = new_end.isoformat()
            
            updated = self.calendar_service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            print(f"✅ Interview rescheduled for {new_date_time}")
            return {'meeting_time': updated.get('start', {}).get('dateTime', '')}
        
        except Exception as e:
            print(f"❌ Error rescheduling: {e}")
            return None
    
    def cancel_interview(self, event_id):
        """Cancel a scheduled interview"""
        try:
            if not self.calendar_service:
                return False
            
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            print(f"✅ Interview cancelled: {event_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error cancelling: {e}")
            return False

# Global scheduler instance
scheduler = MeetScheduler()

if __name__ == "__main__":
    print("Meet Scheduler initialized")