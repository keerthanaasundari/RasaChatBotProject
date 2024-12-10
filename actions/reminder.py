import os
import json
import pickle
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import time

# Google Calendar API authentication function
def authenticate_google_apis():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('C:/Users/z046204/rasa_project/actions/token.json'):
        with open('C:/Users/z046204/rasa_project/actions/token.json', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/z046204/rasa_project/actions/credentials.json', SCOPES)
            creds = flow.run_local_server(port=5055)

        # Save the credentials for the next run
        with open('C:/Users/z046204/rasa_project/actions/token.json', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

# Function to create calendar events
def create_event(service, summary, start_time, end_time, email):
    try:
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [
                {'email': email},
            ],
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")

    except HttpError as error:
        print(f"An error occurred: {error}")

def create_reminders_for_all_employees():
    print("Inside create")
    # Authenticate Google Calendar API
    calendar_service = authenticate_google_apis()

    # Load employee data from employee_data.json
    with open('C:/Users/z046204/rasa_project/actions/employee_data.json') as f:
        employee_data = json.load(f)

    # Example: Reminder for all employees to take a break
    summary = "Take a Break"
    current_time = datetime.utcnow()

    # Set reminder times (example: 9:00 AM, 1:00 PM, 5:00 PM IST)
    reminder_times = [
        {'hour': 3, 'minute': 30, 'summary': 'Morning Break'},
        {'hour': 9, 'minute': 0, 'summary': 'Afternoon Break'},
        {'hour': 11, 'minute': 0, 'summary': 'Evening Break'}
    ]
    
    # Loop through reminder times and create events
    for reminder in reminder_times:
        # Set the reminder time (adjust to IST)
        start_time = current_time.replace(hour=reminder['hour'], minute=reminder['minute'], second=0, microsecond=0) + timedelta(hours=5, minutes=30)
        end_time = start_time + timedelta(minutes=15)  # Break duration: 15 minutes

        for employee in employee_data['employees']:
            # Skip employees who don't have an email
            if employee.get('name') and employee.get('email'):
                email = employee['email']
                create_event(calendar_service, reminder['summary'], start_time.isoformat(), end_time.isoformat(), email)

    print("Calendar reminders have been created for all employees.")

# Function to handle job success or failure logging
def job_listener(event):
    if event.exception:
        print(f'Job {event.job_id} failed')
    else:
        print(f'Job {event.job_id} completed successfully')

# Function to schedule the task using APScheduler
def schedule_reminder_task():
    print(f"Inside reminder task")
    
    # Create an instance of APScheduler's BackgroundScheduler
    scheduler = BackgroundScheduler()

    print(f"Task started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    scheduler.add_job(create_reminders_for_all_employees, 'interval', hours=24, start_date='2024-12-07 15:48:00', id='reminder_job')

    # Add listener to track the status of the scheduled task
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Start the scheduler
    scheduler.start()

    # Keep the scheduler running
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

# Start the reminder scheduler
if __name__ == "__main__":
    schedule_reminder_task()
