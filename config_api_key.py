import os
import json 
import google.generativeai as genai
from google.cloud import aiplatform

with open('config.json', 'r') as file:
    data = json.load(file)
    GOOGLE_API_KEY = data.get('api_key')
    PROJECT_ID = data.get('PROJECT_ID')

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

LOCATION = "us-central1"
aiplatform.init(
    project=PROJECT_ID,
    location=LOCATION
)