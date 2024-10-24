import os
import sqlite3
import time
from .sync import *  # Import the sync library

# Load the .env file
load_dotenv()

# Define the NODE_ID from the .env file
NODE_ID = os.getenv('NODE_ID')

while True:
    # Insert data into the SQLite database
    insert(NODE_ID, 'pH', 10.0)
    time.sleep(5)
