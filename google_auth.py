"""
Google OAuth2 Authentication Handler
Handles login and token management for Google APIs
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

class GoogleAuthHandler:
    """Handle OAuth2 authentication for Google services"""
    
    def __init__(self, credentials_file='oauth_credentials.json', token_file='token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/meetings.space.created',
            'https://www.googleapis.com/auth/gmail.send'
        ]
    
    def get_credentials(self):
        """Get valid credentials for Google APIs"""
        creds = None
        
        # Check if token already exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials don't exist or are invalid, create new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds