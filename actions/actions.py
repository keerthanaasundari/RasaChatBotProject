import mysql.connector
import json
import matplotlib.pyplot as plt
import os
import csv
import re

import base64
import smtplib
import pickle
import time
from threading import Thread
import requests
import spacy
from chatterbot.tagging import PosLemmaTagger

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime
from typing import List
from rasa_sdk.types import DomainDict
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer


import logging

from actions.reminder import schedule_reminder_task
from dotenv import load_dotenv
import os

# Set up Gmail API scope for sending email
SCOPES = ['https://www.googleapis.com/auth/gmail.send']



class ActionChatterBotResponse(Action):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
        print("Initializing ChatterBot...")

        # Initialize ChatterBot
        self.chatbot = ChatBot(
            'RasaBot',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database_uri='mysql://root:root@localhost/employee_productivity',
            logic_adapters=[
                'chatterbot.logic.BestMatch',
                'chatterbot.logic.MathematicalEvaluation'
            ]
        )
        
        # Train ChatterBot with a corpus
        trainer = ChatterBotCorpusTrainer(self.chatbot)
        trainer.train('chatterbot.corpus.english')

    def name(self) -> str:
        return "action_chatterbot_response"

    def read_csv(self, user_message):
        words_in_message = user_message.lower().split()
        print(f"words_in_message: {words_in_message}")
        try:
            print(f"User message: {user_message}")
            # Open the file with UTF-8 encoding (which handles most characters)
            with open('C:/Users/z046204/rasa_project/actions/responses.csv', mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    query_words = row['query'].lower().split()
                    if any(word in query_words for word in words_in_message):
                        response = row['response']
                        response = self.format_links_in_response(response)
                        return response
        except UnicodeDecodeError:
            print("Unicode decoding error encountered. Trying different encoding.")
            try:
                # Fall back to ISO-8859-1 encoding if UTF-8 fails
                with open('C:/Users/z046204/rasa_project/actions/responses.csv', mode='r', encoding='ISO-8859-1') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        query_words = row['query'].lower().split()
                        print(f"query_words: {query_words}")
                        if any(word in query_words for word in words_in_message):
                            response = row['response']
                            response = self.format_links_in_response(response)
                            return response
            except Exception as e:
                print(f"Error reading CSV file with fallback encoding: {e}")
        except Exception as e:
            print(f"Error reading CSV file: {e}")

        return None

    def format_links_in_response(self, response):
        # This function will find URLs in the response and wrap them in anchor tags
        url_pattern = r'(https?://\S+)'
        formatted_response = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', response)
        return formatted_response

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Get the user's input from the tracker (latest message from the user)
        user_message = tracker.latest_message.get('text')
        print(f"User message from run: {user_message}")

        # First, check for a predefined response in the CSV file
        predefined_response = self.read_csv(user_message)
        
        if predefined_response:
            # If a predefined response is found in the CSV, send it
            dispatcher.utter_message(text=predefined_response)
        else:
            # Otherwise, fall back to ChatterBot for a response
            bot_response = self.chatbot.get_response(user_message)
            dispatcher.utter_message(text=str(bot_response))

        return []
def authenticate_gmail_api():
    creds = None
    # Check if token.json exists to store the user's access and refresh tokens
    if os.path.exists('C:/Users/z046204/rasa_project/actions/token.json'):
        with open('C:/Users/z046204/rasa_project/actions/token.json', 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials are expired or not available, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If no valid credentials, initiate OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/z046204/rasa_project/actions/credentials.json', SCOPES)
            creds = flow.run_local_server(port=5055)  # Redirect URI is localhost:5000
    
        # Save the credentials for future use
        with open('C:/Users/z046204/rasa_project/actions/token.json', 'wb') as token:
            pickle.dump(creds, token)
    
    # Return authenticated Gmail API service
    return build('gmail', 'v1', credentials=creds)

def load_employee_data(filename='C:/Users/z046204/rasa_project/actions/employee_data.json'):
    """
    Load the employee data from the provided JSON file.
    """
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def generate_burnout_chart(burnout_data):
    """
    Generate a burnout chart based on employee's burnout data.
    """
    dates = [entry['date'] for entry in burnout_data]
    stress_levels = [entry['stress_level'] for entry in burnout_data]

    # Map stress levels to numerical values
    stress_map = {'Low': 1, 'Moderate': 2, 'High': 3, None: 0}
    stress_values = [stress_map.get(level, 0) for level in stress_levels]

    # Plot burnout data
    plt.figure(figsize=(10, 6))
    plt.plot(dates, stress_values, marker='o', linestyle='-', color='b')
    plt.title("Employee Burnout Over Time")
    plt.xlabel("Date")
    plt.ylabel("Stress Level")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot as an image
    chart_filename = "burnout_chart.png"
    plt.savefig(chart_filename)
    plt.close()  # Close the plot to free up memory
    return chart_filename

def create_message_with_attachment(sender, to, subject, body, attachment_file):
    """
    Create an email message with an attachment.
    """
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = to
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Attach the burnout chart image
    with open(attachment_file, 'rb') as attachment:
        img_data = MIMEImage(attachment.read())
        img_data.add_header('Content-Disposition', 'attachment', filename=attachment_file)
        message.attach(img_data)

    # Encode the message in base64 format for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(service, message):
    """Send the email using Gmail API."""
    try:
        service.users().messages().send(userId="me", body=message).execute()
        print("Email sent successfully.")
    except Exception as error:
        print(f"An error occurred: {error}")

class ActionSendBurnoutEmail(Action):
    def name(self) -> str:
        return "action_send_burnout_email"
    
    def run(self, dispatcher: CollectingDispatcher, tracker, domain: dict) -> list:
        employee_name = tracker.get_slot("name")
        employee_id = tracker.get_slot("employee_id")
        
        if not employee_name:
            dispatcher.utter_message(text="Employee name not found!")
            return []

        # Load employee data from the JSON file
        employee_data = load_employee_data()

        # Search for the specific employee by ID
        employee = next((e for e in employee_data['employees'] if e['name'] == employee_name), None)

        if not employee:
            dispatcher.utter_message(text="Employee not found!")
            return []

        # Get the burnout data for the specific employee
        burnout_data = employee.get('burnout', [])

        if not burnout_data:
            dispatcher.utter_message(text="No burnout data available for this employee.")
            return []

        # Authenticate and get Gmail API service
        service = authenticate_gmail_api()

        # Generate burnout chart for the employee
        chart_filename = generate_burnout_chart(burnout_data)

        # Email details
        sender_email = "keerthanaakalyan@gmail.com"  # Replace with your email
        receiver_email = employee.get(email)  # Replace with recipient's email
        subject = f"Burnout Report for {employee_name}"
        body = f"Attached is the burnout report chart for {employee_name}."

        # Create the email message with the chart attached
        message = create_message_with_attachment(sender_email, receiver_email, subject, body, chart_filename)

        # Send the email using Gmail API
        send_email(service, message)

        # Remove the temporary chart image file after sending the email
        os.remove(chart_filename)

        dispatcher.utter_message(text=f"Burnout report for {employee_name} has been sent via email.")

        return []
class ActionSendBurnoutEmailAll(Action):
    def name(self) -> str:
        return "action_send_burnout_email_all"
    
    def run(self, dispatcher: CollectingDispatcher, tracker, domain: dict) -> list:
        # Load employee data from the JSON file
        employee_data = load_employee_data()

        # Authenticate and get Gmail API service
        service = authenticate_gmail_api()

        # List to hold messages for each employee
        chart_filename = "burnout_chart.png"

        for employee in employee_data['employees']:
            # Get the burnout data and email for each employee
            burnout_data = employee.get('burnout', [])
            employee_name = employee.get('name')
            receiver_email = employee.get('email')

            if not burnout_data:
                continue  # Skip employees with no burnout data

            if not receiver_email:
                continue  # Skip employees with no email address

            # Generate burnout chart for the employee
            chart_filename = generate_burnout_chart(burnout_data)

            # Email details
            sender_email = "keerthanaakalyan@gmail.com"  # Replace with your email
            subject = f"Burnout Report for {employee_name}"
            body = f"Attached is the burnout report chart for {employee_name}."

            # Create the email message with the chart attached
            message = create_message_with_attachment(sender_email, receiver_email, subject, body, chart_filename)

            # Send the email using Gmail API
            send_email(service, message)

            # Remove the temporary chart image file after sending the email
            os.remove(chart_filename)

        dispatcher.utter_message(text="Burnout reports for all employees have been sent via email.")

        return []

class ActionTrackTask(Action):
    def name(self):
        return "action_track_task"
    
    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # Extract the task description from the user input
        task = tracker.latest_message['text']
        
        # Save the log to MySQL
        self.save_log("track_task", task)
        
        dispatcher.utter_message(text="Task has been recorded successfully!")
        return []

    def save_log(self, action, message):
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",  # your MySQL server
            user="root",  # your MySQL user
            password="root",  # your MySQL password
            database="employee_productivity"  # your database name
        )
        cursor = conn.cursor()

        # Insert the log data into the MySQL table
        cursor.execute("INSERT INTO logs (action, message) VALUES (%s, %s)", (action, message))

        # Commit the transaction
        conn.commit()

        # Close the connection
        cursor.close()
        conn.close()

class ActionCheckAbsenteeism(Action):
    def name(self) -> str:
        return "action_check_absenteeism"

    def run(self, dispatcher, tracker, domain):
        employee_name = tracker.get_slot("name")
        
        # Load the existing employee data from the JSON file
        with open('C:/Users/z046204/rasa_project/actions/employee_data.json', 'r') as f:
            data = json.load(f)

        # Find the employee
        employee = next((emp for emp in data["employees"] if emp["name"] == employee_name), None)
        
        if employee:
            absences = employee.get("absences", [])
            if absences:
                absence_details = "\n".join([f"Date: {a['date']}, Reason: {a['reason']}" for a in absences])
                dispatcher.utter_message(f"Your absenteeism records for the last month:\n{absence_details}")
            else:
                dispatcher.utter_message("You have no absenteeism records for the last month.")
        else:
            dispatcher.utter_message("No records found for you.")
        
        return []

class ActionGivePersonalizedHealthRecommendation(Action):
    def name(self) -> str:
        return "action_give_health_recommendation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Get the name from the user's input
        user_name = tracker.get_slot("name")

        # Load the data from 'data.json'
        with open('C:/Users/z046204/rasa_project/actions/employee_data.json', 'r') as f:
            data = json.load(f)

        # Search for the user in the data
        user_data = None
        for employee in data['employees']:
            if employee['name'].lower() == user_name.lower():
                user_data = employee
                break

        if user_data:
            # Generate personalized recommendations based on the user's data
            recommendations = self.generate_health_recommendations(user_data)
            dispatcher.utter_message("\n".join(recommendations))
        else:
            dispatcher.utter_message(f"Sorry, I couldn't find information for {user_name}. Please check your name and try again.")

        return []

    def generate_health_recommendations(self, user_data):
        recommendations = []

        # Provide health recommendation based on work hours
        if user_data["work_hours"] > 8:
            recommendations.append("It's important to take regular breaks and stretch after long hours of sitting.")

        # Provide recommendation based on work environment
        if user_data["work_environment"] == "remote":
            recommendations.append("Since you work from home, make sure to create a dedicated workspace to avoid burnout.")
        elif user_data["work_environment"] == "office":
            recommendations.append("In an office environment, be sure to move around regularly to keep your energy levels up.")

        # Provide recommendation based on activity level
        if user_data["activity_level"] == "sit":
            recommendations.append("Consider using a standing desk or taking short walks during the day to improve circulation.")
        elif user_data["activity_level"] == "stand":
            recommendations.append("It's great that you stand during the day! Just ensure you're not standing for too long without moving around.")
        elif user_data["activity_level"] == "walk":
            recommendations.append("Walking around is great! Try to incorporate some stretching to avoid muscle strain.")

        # Provide recommendation based on stress level
        if user_data["max_stress_level"] == "high":
            recommendations.append("Since your work is stressful, practice deep breathing exercises and try to schedule relaxation time.")
        elif user_data["max_stress_level"] == "low":
            recommendations.append("Great to see your moderate stress, encouraging make it to low by practicing mindfulness and meditation.")
        elif user_data["max_stress_level"] == "low":
            recommendations.append("Your low-stress work environment is great for your mental health. Keep it up!")

        # Provide recommendation based on break habits
        if user_data["break_habits"] == "regular":
            recommendations.append("Great! Regular breaks can boost productivity and mental well-being.")
        elif user_data["break_habits"] == "irregular":
            recommendations.append("Try to take regular breaks to prevent burnout. Even a 5-minute walk can help refresh your mind.")

        return recommendations

class ActionGivePersonalizedTips(Action):
    def name(self) -> str:
        return "action_give_personalized_tips"

    def run(self, dispatcher, tracker, domain):
        # Extract values from slots
        work_hours = tracker.get_slot('work_hours')
        work_environment = tracker.get_slot('work_environment')
        activity_level = tracker.get_slot('activity_level')

        recommendations = []

        # Personalized productivity and focus recommendations based on slots

         #Ensure work_hours is a float
        if isinstance(work_hours, str):
            work_hours = float(work_hours)

        # Work hours-based recommendations
        if work_hours and work_hours > 8:
            recommendations.append("Since you work more than 8 hours a day, it's important to take regular breaks to avoid burnout.")

        # Environment-based recommendations
        if work_environment and work_environment == "remote":
            recommendations.append("As you work from home, ensure your workspace is free from distractions and maintain a consistent schedule.")
        elif work_environment and work_environment == "office":
            recommendations.append("In an office, it's helpful to take short walks to stay energized. Consider using a standing desk.")

        # Activity level-based recommendations
        if activity_level and activity_level == "sit":
            recommendations.append("If you're sitting for long periods, try using a standing desk or taking short walks.")
        elif activity_level and activity_level == "stand":
            recommendations.append("Standing is great! But make sure to move around every 30 minutes to avoid fatigue.")
        elif activity_level and activity_level == "walk":
            recommendations.append("Walking regularly is awesome! Try incorporating stretching to avoid muscle strain.")

        # Provide personalized recommendations to the user
        if recommendations:
            dispatcher.utter_message("\n".join(recommendations))
        else:
            dispatcher.utter_message("You're doing great! Keep up the good work.")

        return []

