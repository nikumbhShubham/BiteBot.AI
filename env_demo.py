import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('COHERE_API_KEY')

if api_key:
    print(api_key)
else:
    print("COHERE_API_KEY environment variable not found.")