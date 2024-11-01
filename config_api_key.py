import os
import json 
import google.generativeai as genai

with open('config.json', 'r') as file:
    data = json.load(file)
    GOOGLE_API_KEY = data.get('api_key')

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)