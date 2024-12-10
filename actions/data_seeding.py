import requests
from dotenv import load_dotenv
import os
import csv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Replace these with your actual API Key and CSE ID
API_KEY = os.getenv('API_KEY')
CSE_ID = os.getenv('CSE_ID')

# Function to perform Google Custom Search
def google_search(query):
    # Google Custom Search API endpoint
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}"
    
    print(f"url: {url}")
    
    # Make the API request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        search_results = response.json()
        return search_results.get('items', [])  # Ensure 'items' is present
    else:
        print(f"Error fetching search results: {response.status_code}")
        return []

# Function to extract useful information from the search results
def extract_info_from_results(results):
    # Extract useful information (like titles, snippets, and links) from the search results
    extracted_data = []
    for result in results:
        title = result['title']
        snippet = result.get('snippet', 'No snippet available')
        link = result['link']
        extracted_data.append((title, snippet, link))
    
    return extracted_data

# Function to write the data to a CSV file
def write_to_csv(data, query):
    # Define CSV file path
    csv_file = "responses.csv"
    
    # Open CSV file in append mode with UTF-8 encoding to handle special characters
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header only if the file is empty
        if file.tell() == 0:  # Check if file is empty before writing header
            writer.writerow(["query", "response"])
        
        # Write the query and the response from the search results
        for item in data:
            title, snippet, link = item
            response = f"{snippet}\nLink: {link}"
            writer.writerow([query, response])

# Main logic
queries = ["fever", "headache", "cough", "malaria", "tuberculosis", "cancer", "COVID-19", "pneumonia", "diabetes", "cold", "sore throat", "flu"]  # Example health-related queries

for query in queries:
    # Fetch search results from Google Custom Search
    results = google_search(query)

    if results:
        # Extract useful information from the search results
        data = extract_info_from_results(results)
        
        # Write data to the CSV file
        write_to_csv(data, query) 
        print(f"Data for query '{query}' written to CSV.")
    else:
        print(f"No results found for query: {query}")

    # Print the extracted data for review
    for item in data:
        print(f"Title: {item[0]}")
        print(f"Snippet: {item[1]}")
        print(f"Link: {item[2]}")
        print("-----")
