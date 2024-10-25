import firebase_admin
from firebase_admin import credentials, firestore
import sentry_sdk
import re
import matplotlib.pyplot as plt
import numpy as np

# Initialize the app with a service account, granting admin privileges
#service_account_path = './testemonit-b47a7-a661a9bda465.json'  # Path to your service account key
service_account_path = './testemonit-b47a7-firebase-adminsdk-pzfoa-8397104377.json'

cred = credentials.Certificate(service_account_path)

firebase_admin.initialize_app(cred)

# Accessing Firestore
db = firestore.client()

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


def list_collections():
    try:
        collections = db.collections()
        collection_names = [collection.id for collection in collections]
        return collection_names  # Return the list of collection names
    except Exception as error:
        print('Error listing collections:', error)
        return []  # Return an empty list in case of error

def get_collection_size(collection_name):
    try:
        snapshot = db.collection(collection_name).get()  # Get the collection
        return len(snapshot)  # Return the number of documents in the collection
    except Exception as error:
        print('Error getting collection size:', error)
        raise error  # Re-throw the error for further handling

def parse_ipfer_results(file_path):
    results = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    current_result = {}
    for line in lines:
        # Check for the lines that start with "[ ID]"
        if line.startswith('[ ID]'):
            # If we already have data, save the current result to the list
            if current_result:
                results.append(current_result)
                current_result = {}

            # Extract total transfer and bitrate for the last interval
            total_match = re.search(r'\[  \d+\]   0.00-(\d+\.\d+)  sec  ([\d\.]+) GBytes  ([\d\.]+) Gbits/sec', line)
            if total_match:
                current_result['total_duration'] = total_match.group(1)
                current_result['total_transfer'] = total_match.group(2) + ' GBytes'
                current_result['total_bitrate'] = total_match.group(3) + ' Gbits/sec'

        # Extract interval data
        interval_match = re.search(r'\[  \d+\]   (\d+\.\d+)-(\d+\.\d+)   sec  ([\d\.]+) GBytes  ([\d\.]+) Gbits/sec', line)
        if interval_match:
            interval_data = {
                'start_time': interval_match.group(1),
                'end_time': interval_match.group(2),
                'transfer': interval_match.group(3) + ' GBytes',
                'bitrate': interval_match.group(4) + ' Gbits/sec',
            }
            if 'intervals' not in current_result:
                current_result['intervals'] = []
            current_result['intervals'].append(interval_data)

    # Append the last result if there's any
    if current_result:
        results.append(current_result)

    return results


def plot_results(transfer_array, bitrate_array):
    # Convert transfer and bitrate to numeric values
    transfer_numeric = [float(x.split()[0]) for x in transfer_array]
    bitrate_numeric = [float(x.split()[0]) for x in bitrate_array]
    
    transfer_numeric_pumba = [float(x.split()[0]) for x in transfer_array_pumba]
    bitrate_numeric_pumba = [float(x.split()[0]) for x in bitrate_array_pumba]

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plotting
    x = range(len(transfer_numeric))  # X values
    ax.plot(x, transfer_numeric, label='Transfer (GBytes)', marker='o')
    ax.plot(x, bitrate_numeric, label='Bitrate (Gbits/sec)', marker='x')
    
    ax.plot(x, transfer_numeric_pumba, label='Transfer Pumba (GBytes)', marker='+')
    ax.plot(x, bitrate_numeric_pumba, label='Bitrate Pumba (Gbits/sec)', marker='*')

    # Add labels and title
    ax.set_xlabel('Intervalo')
    ax.set_ylabel('Valores')
    ax.set_title('Transfer e Bitrate ao Longo do Tempo')
    ax.legend()

    # Set x-ticks with vertical alignment
    ax.set_xticks(x)
    ax.set_xticklabels([f'Intervalo {i+1}' for i in x], rotation=90, ha='right')  # ha for horizontal alignment
    
    # Adjust layout
    fig.tight_layout()
    
    # Save the plot
    plt.savefig('/app_observer/transfer_bitrate_plot.png')  # Adjust path as needed
    plt.close()

    print('call to plot ####################################################################')

def parsed_results_to_arrays( parsed_results ):
    for result in parsed_results:
        
        transfer_array = []
        bitrate_array = []

        for interval in result['intervals']:
            start_time = interval['start_time']
            end_time = interval['end_time']
            transfer = interval['transfer']
            bitrate = interval['bitrate']

            transfer_array.append( transfer )
            bitrate_array.append( bitrate )
    
    return transfer_array, bitrate_array

if __name__ == "__main__":
    
    collection_names = list_collections()

    for collection in collection_names:

        try:
            size = get_collection_size(collection)
            print(f'Collection name {collection} size: {size}')
            print('--------------------------------------------')

            sentry_sdk.capture_message( f'Collection name {collection} size: {size}' )

        except Exception as error:
            print('Error getting collection size:', error)

    file_path_pumba = 'iperf_results_10_com_pumba.txt'
    file_path = 'iperf_results_10_sem_pumba.txt'

    parsed_results = parse_ipfer_results(file_path)
    parsed_results_pumba = parse_ipfer_results(file_path_pumba)
    
    transfer_array, bitrate_array = parsed_results_to_arrays( parsed_results )
    transfer_array_pumba, bitrate_array_pumba = parsed_results_to_arrays( parsed_results_pumba )
 
    print(f' transfer_array {transfer_array} ')
    print(f' bitrate_array {bitrate_array} ')

    print(f' transfer_array_pumba {transfer_array_pumba} ')

    print(f' bitrate_array_pumba {bitrate_array_pumba} ')

    plot_results( transfer_array, bitrate_array )