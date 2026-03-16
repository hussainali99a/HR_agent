"""
Meet Scheduler Module
Schedules Google Meet interviews for candidates
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
from datetime import timedelta
import uuid
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_CALENDAR_ID, INTERVIEW_TIMEZONE, INTERVIEW_DURATION_MINUTES
from database import db

class MeetScheduler:
    """Handles Google Meet scheduling"""
    
    def __init__(self):
        self.credentials_file = GOOGLE_CREDENTIALS_FILE
        self.calendar_id = GOOGLE_CALENDAR_ID
        self.timezone = INTERVIEW_TIMEZONE
        self.duration = INTERVIEW_DURATION_MINUTES
        self.service = self.initialize_service()
    
    def initialize_service(self):
        """Initialize Google Calendar service"""
        try:
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES)
            
            service = build('calendar', 'v3', credentials=credentials)
            print("✅ Google Calendar service initialized")
            return service
        
        except Exception as e:
            print(f"❌ Error initializing Google Calendar: {e}")
            print(f"⚠️  Make sure credentials.json is in the correct location: {self.credentials_file}")
            return None
    
    def schedule_interview(self, candidate_name, candidate_email, job_title, 
                          interview_date_time, candidate_id=None):
        """
        Schedule an interview meeting for a candidate
        
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
            if not self.service:
                print("❌ Google Calendar service not available")
                return None
            
            # Calculate end time
            interview_end = interview_date_time + timedelta(minutes=self.duration)
            
            # Create event
            event = {
                'summary': f'Interview: {candidate_name} - {job_title}',
                'description': f'HR Interview for {job_title} position\nCandidate: {candidate_name}\nEmail: {candidate_email}',
                'start': {
                    'dateTime': interview_date_time.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': interview_end.isoformat(),
                    'timeZone': self.timezone,
                },
                'attendees': [
                    {'email': candidate_email, 'responseStatus': 'needsAction'}
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }
            
            # Insert event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='eventCreator'
            ).execute()
            
            # Extract meeting details
            meeting_link = created_event.get('hangoutLink', '')
            meeting_time = created_event.get('start', {}).get('dateTime', '')
            
            print(f"✅ Interview scheduled for {candidate_name}")
            print(f"   Time: {meeting_time}")
            print(f"   Link: {meeting_link}")
            
            # Log to database
            if candidate_id:
                db.log_meeting(candidate_id, meeting_time, meeting_link, "SCHEDULED")
            
            return {
                'meeting_link': meeting_link,
                'meeting_time': meeting_time,
                'event_id': created_event.get('id')
            }
        
        except Exception as e:
            print(f"❌ Error scheduling interview: {e}")
            return None
    
    def reschedule_interview(self, event_id, new_date_time):
        """Reschedule an existing interview"""
        try:
            if not self.service:
                print("❌ Google Calendar service not available")
                return None
            
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update time
            new_end = new_date_time + timedelta(minutes=self.duration)
            
            event['start']['dateTime'] = new_date_time.isoformat()
            event['end']['dateTime'] = new_end.isoformat()
            
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='eventCreator'
            ).execute()
            
            print(f"✅ Interview rescheduled for {new_date_time}")
            
            return {
                'meeting_link': updated_event.get('hangoutLink', ''),
                'meeting_time': updated_event.get('start', {}).get('dateTime', '')
            }
        
        except Exception as e:
            print(f"❌ Error rescheduling interview: {e}")
            return None
    
    def cancel_interview(self, event_id):
        """Cancel a scheduled interview"""
        try:
            if not self.service:
                print("❌ Google Calendar service not available")
                return False
            
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='eventCreator'
            ).execute()
            
            print(f"✅ Interview cancelled: {event_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error cancelling interview: {e}")
            return False
    
    def get_available_slots(self, date, num_slots=5):
        """
        Get available time slots for a given date
        
        Args:
            date: datetime.date object
            num_slots: Number of slots to return
        
        Returns:
            List of available datetime objects
        """
        try:
            if not self.service:
                print("❌ Google Calendar service not available")
                return []
            
            # Define working hours: 10 AM to 5 PM
            working_start = 10
            working_end = 17
            slot_duration = 1  # 1-hour slots
            
            date_str = date.strftime('%Y-%m-%d')
            
            # Check existing events for this date
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=f'{date_str}T00:00:00',
                timeMax=f'{date_str}T23:59:59',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            existing_events = events_result.get('items', [])
            
            # Generate available slots
            available_slots = []
            current_hour = working_start
            
            while current_hour < working_end and len(available_slots) < num_slots:
                slot_time = datetime.datetime.combine(
                    date,
                    datetime.time(current_hour, 0, 0)
                )
                
                # Check if slot conflicts with existing events
                is_available = True
                for event in existing_events:
                    event_start = datetime.datetime.fromisoformat(
                        event['start'].get('dateTime', '').replace('Z', '+00:00')
                    )
                    event_end = datetime.datetime.fromisoformat(
                        event['end'].get('dateTime', '').replace('Z', '+00:00')
                    )
                    
                    # Check for overlap
                    if slot_time < event_end and (slot_time + timedelta(hours=slot_duration)) > event_start:
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(slot_time)
                
                current_hour += slot_duration
            
            return available_slots
        
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return []

# Global scheduler instance
scheduler = MeetScheduler()

if __name__ == "__main__":
    # Test the scheduler
    print("Meet Scheduler Test\n")
    
    # Test available slots
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    slots = scheduler.get_available_slots(tomorrow)
    
    print(f"Available slots for {tomorrow}:")
    for slot in slots[:3]:
        print(f"  - {slot.strftime('%H:%M')}")
