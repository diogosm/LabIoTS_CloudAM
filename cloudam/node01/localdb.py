import os
import sqlite3
import time
from localdbsharedlib import *  # Import the sync library
from dotenv import load_dotenv
import logging, sys

# Load the .env file
load_dotenv()

# Define the NODE_ID from the .env file
NODE_ID = os.getenv('NODE_ID')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True, handlers=[logging.StreamHandler(sys.stdout)])

## dropa e cria a tabela antes
logging.info("dropando table...")
dropa_table()
logging.info("criando tabela...")
create_table()

logging.info("iniciando insercoes")
cont = 1
while True:
    # Insert data into the SQLite database
    logging.info(f"inserindo {cont}-esimo dado...")
    insert(NODE_ID, 'pH', 10.0)
    time.sleep(5)
