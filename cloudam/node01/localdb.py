import os
import sqlite3
import time
from localdbsharedlib import *  # Import the sync library
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Define the NODE_ID from the .env file
NODE_ID = os.getenv('NODE_ID')

## dropa e cria a tabela antes
print("dropando table...", flush=True)
dropa_table()
print("criando tabela...", flush=True)
create_table()

print("iniciando insercoes", flush=True)
cont = 1
while True:
    # Insert data into the SQLite database
    print("inserindo ${cont}-esimo dado...", flush=True)
    insert(NODE_ID, 'pH', 10.0)
    time.sleep(5)
