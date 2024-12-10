# RasaChatBotProject

This Rasa chatbot project is designed to provide productivity tips, stress relief, self-care advice, disease and fever-related information, as well as personalized health recommendations. The bot responds to users' queries regarding their productivity, mental health, and physical well-being, offering tailored suggestions based on the provided context.

# Project Structure

**Intents**
The chatbot includes several intents that cover a range of topics related to productivity, health, and personal well-being:

**productivity_tips**: A collection of tips and suggestions to help users improve productivity.
**focus_tips:** Tips to enhance focus and concentration during work or study.
****ask_for_stress_relief:** Advice on how to relieve stress.
**ask_self_care_tips:** Guidance on self-care to maintain physical and mental health.
**ask_disease_info:** Information about common diseases and health conditions.
**ask_fever_info:** Specific information related to fever symptoms and causes.

# Entities
Entities are variables that capture specific information from user input. These are used to tailor responses and take appropriate actions based on the context.

**name:** The name of the user or an individual involved.
**employee_id:** Unique identifier for an employee in a work setting.
**date:** Date associated with a query or task.
**reason:** The reason for a particular action or request.
**stress_level:** Level of stress experienced by the user (e.g., low, moderate, high).
**work_hours:** Number of hours worked by the user.
**work_environment:** Description of the user's work environment (e.g., remote, office).
**activity_level:** The user's physical activity level (e.g., sedentary, active).

# Actions
Actions define the operations the chatbot can perform, based on user input and entities. These actions can help automate tasks or provide personalized recommendations.

**action_send_burnout_email_all:** Sends a burnout alert email to all employees if certain criteria are met.
**action_check_absenteeism:** Checks absenteeism records and provides insights.
**action_track_task:** Tracks the progress of a specific task.
**action_send_burnout_email:** Sends a personalized burnout alert email to an individual.
**action_start_reminder_scheduler:** Starts a reminder scheduler to prompt the user about tasks or wellness activities.
**action_give_health_recommendation:** Provides health recommendations based on the user's input (e.g., stress levels, work hours).
**action_give_personalized_tips:** Delivers personalized tips for better productivity, stress management, and self-care.
**action_chatterbot_response:** Provides conversational responses based on pre-configured chatbot behavior.

# To get started with this Rasa chatbot project, you need to have Python 3.7+ and Rasa installed.

**Clone the repository:**
git clone https://github.com/yourusername/productivity-chatbot.git
cd productivity-chatbot

**Install required dependencies:**
pip install -r requirements.txt

**Install Rasa**:
pip install rasa

**Initialize the Rasa project (if not already initialized):**
rasa init

**Train the model:**
rasa train

**Start the chatbot:**
rasa run

**Environment Setup for API, CSI Key, and OAuth Credentials**
In order to integrate with external services such as Google Calendar and Gmail APIs, you will need to configure the necessary credentials and API keys. This section outlines how to set up environment variables for API keys, OAuth credentials, and other sensitive data used in the Rasa chatbot project.

**Environment Variables Configuration**
Rasa uses environment variables to securely manage sensitive data such as API keys, service credentials, and other configuration settings required for integrations. You can store these values in an .env file, which is not tracked in source control to ensure the security of your keys.

**Steps to Configure Environment Variables**
Configuring OAuth API with Google Credentials
To integrate your Rasa chatbot with Google services like Google Calendar and Gmail, you'll need to authenticate using OAuth 2.0 credentials. Google provides a credentials.json file when you enable the APIs on Google Cloud Console. Here's how to set it up:

**1. Set Up Google API Credentials**
Follow these steps to obtain the credentials.json file:

Create a Project on Google Cloud Console:

Visit the Google Cloud Console.
Create a new project or select an existing one.
**2. Enable APIs:**

Navigate to APIs & Services > Library.
Enable the Google Calendar API and Gmail API (or any other APIs you wish to use with your bot).
**3. Create OAuth 2.0 Credentials:**
Go to APIs & Services > Credentials.
Click Create Credentials and select OAuth 2.0 Client IDs.
Choose the application type (e.g., Web application or Desktop app).
Under Authorized redirect URIs, add http://localhost:8080/ (or another port if using a different setup).
Once created, download the credentials.json file.
**4. Store the credentials.json File:**

Place the downloaded credentials.json file in the root directory of your Rasa project. This file contains the client ID, client secret, and necessary configuration for OAuth 2.0 authentication.
Create an .env file in the root of your Rasa project. This file will hold all your API keys and credentials.

**Add the following environment variables in the .env file for Google Calendar API, Gmail API, and other related services:**

# Google API OAuth 2.0 credentials
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REFRESH_TOKEN=your-google-refresh-token

# Calendar API Scopes (Optional)
GOOGLE_CALENDAR_SCOPE=https://www.googleapis.com/auth/calendar
GOOGLE_GMAIL_SCOPE=https://www.googleapis.com/auth/gmail.readonly

# API keys for external services
API_KEY=your-api-key-here
CSI_KEY=your-csi-key-here
