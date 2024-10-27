import os
import json 

with open('config.json', 'r') as file:
    data = json.load(file)
    GOOGLE_API_KEY = data.get('api_key')

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY