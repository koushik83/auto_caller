from twilio.rest import Client
import logging
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
VERIFIED_PHONE_NUMBER = os.getenv('VERIFIED_PHONE_NUMBER')

def make_test_call(ngrok_url):
    """Make test call with monitoring"""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    try:
        print("\nInitiating call...")
        
        # Make the call
        call = client.calls.create(
            url=f"{ngrok_url}/voice",
            to=VERIFIED_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            record=True
        )
        
        print(f"\nCall initiated!")
        print(f"Call SID: {call.sid}")
        print("\nMonitoring call status...")
        
        # Monitor the call status
        while True:
            # Get updated call status
            call_status = client.calls(call.sid).fetch().status
            print(f"\nCall Status: {call_status}")
            
            # Exit if call is complete or failed
            if call_status in ['completed', 'failed', 'busy', 'no-answer']:
                print(f"\nCall ended with status: {call_status}")
                break
            
            # Wait before checking again
            time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    print("\nAI Conversation Test")
    print("===================")
    
    # Get ngrok URL from user
    print("\nMake sure both are running:")
    print("1. Flask server (python app.py)")
    print("2. ngrok (ngrok http 5000)")
    
    # Get ngrok URL
    ngrok_url = input("\nEnter your ngrok URL (e.g., https://xxxx.ngrok.io): ").strip()
    
    # Remove trailing slash if present
    if ngrok_url.endswith('/'):
        ngrok_url = ngrok_url[:-1]
    
    # Make the call
    success = make_test_call(ngrok_url)
    
    if success:
        print("\nCall completed successfully!")
    else:
        print("\nCall failed. Check the error messages above.")