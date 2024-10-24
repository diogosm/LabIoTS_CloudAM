import firebase_admin
from firebase_admin import credentials, firestore
from time import sleep
import os
from dotenv import load_dotenv
import logging
import sentry_sdk

# .env variables
load_dotenv()

# Firebase Admin
cred = credentials.Certificate('testemonit-b47a7-a661a9bda465.json')
#app = firebase_admin.initialize_app(cred, name="teste")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

NODE_ID = os.getenv('NODE_ID')
NAME = os.getenv('NAME')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sentry_sdk.init(
    dsn="https://fd0e33d2043ff6bb5f4a2b8aac860567@o4508179211550720.ingest.us.sentry.io/4508179262406656",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

def send_data():
    try:
        # verifica se device ja existe
        dispositivos_collection = db.collection('devices')
        dispositivo_query = dispositivos_collection.where('node_id', '==', NODE_ID).stream()

        # checa device
        dispositivo_exists = False
        for doc in dispositivo_query:
            dispositivo_exists = True
            logging.info(f"verificando {doc}")
            break

        # device nao existe, cria
        if not dispositivo_exists:
            dispositivos_collection.document().set({
                'node_id': NODE_ID,
                'name': NAME,
                'status': 'Online',
                'latitude': 0.00,
                'longitude': 0.00,
                'last_updated': firestore.SERVER_TIMESTAMP
            })
            logging.info(f"Created new device with node_id: {NODE_ID}")
        else:
            logging.info(f"Device {NODE_ID} already exists")

        # Query or create data types pH and Temperatura
        data_types = db.collection('data_type')
        data_types_ids = {}

        for data_type in ['pH', 'Temperatura']:
            data_type_query = data_types.where('type', '==', data_type).stream()
            data_type_exists = False
            for doc in data_type_query:
                data_types_ids[data_type] = doc.id
                data_type_exists = True
                break

            if not data_type_exists:
                new_doc_ref = data_types.document()
                new_doc_ref.set({
                    'type': data_type,
                    'description': f'Dados de {data_type}',
                    'last_updated': firestore.SERVER_TIMESTAMP
                })
                data_types_ids[data_type] = new_doc_ref.id
                logging.info(f"Created new data_type: {data_type}")

        # Envia dados
        logging.info(f"try to send new data...")
        dados_collection = db.collection('data')

        dados_collection.document().set({
            'valor': 7.0,
            'tipo_dados_id': data_types_ids['pH'],
            'device_id': NODE_ID,
            'last_updated': firestore.SERVER_TIMESTAMP
        })
        logging.info(f"pH data sent for device {NODE_ID}")

        dados_collection.document().set({
            'valor': 39.0,
            'tipo_dados_id': data_types_ids['Temperatura'],
            'device_id': NODE_ID,
            'last_updated': firestore.SERVER_TIMESTAMP
        })
        logging.info(f"Temperature data sent for device {NODE_ID}")
        sentry_sdk.capture_message( f"Temperature data sent for device {NODE_ID}" )

    except Exception as e:
        sentry_sdk.capture_exception(e)
        logging.error(f"Error sending data: {str(e)}")

if __name__ == "__main__":
    while True:
        send_data()
        sleep(30)
