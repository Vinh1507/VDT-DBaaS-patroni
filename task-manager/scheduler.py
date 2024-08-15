import os
from dotenv import load_dotenv
import requests
import time
import json
import re

# Load environment variables from .env file
load_dotenv()

# Load configurations from environment variables
IPs = os.getenv('IPS', '192.168.144.133,192.168.144.135,192.168.144.136').split(',')
PORT = int(os.getenv('PORT', 8008))
CONFIG_FILE_PATH = os.getenv('CONFIG_FILE_PATH', './pgbouncer.ini')
print(CONFIG_FILE_PATH)

def get_pgbouncer_db_config(): 
    with open(CONFIG_FILE_PATH, 'r') as file:
        text = file.read()

    # Regular expression to extract the content between the markers
    match = re.search(r';; \[config cluster: begin\](.*?);; \[config cluster: end\]', text, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        return extracted_text
    else:
        return None

def get_pgbouncer_primary_ip():
    connection_string = get_pgbouncer_db_config()

    print(connection_string)

    if connection_string is None:
        return None

    host_match = re.search(r'host=(\d+\.\d+\.\d+\.\d+)', connection_string)

    if host_match:
        host_value = host_match.group(1)
        return host_value
    else:
        return None

def update_cluster_state(patroni_primary_host):
    # Define the URL and headers
    try:
        url = os.getenv('FLASK_API_URL')
        headers = {'Content-Type': 'application/json'}

        # Define the data to be sent in the request
        data = {
            "extra_vars": {
                "patroni_primary_host": patroni_primary_host
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Print the response from the server
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Failed:", response.status_code, response.text)
    except e:
        print(e)

def send_logging():
    url = os.getenv('LOGGING_API_URL')
    headers = {'Content-Type': 'application/json'}
    data = {
        "logging": {
            "status": 'running'
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

while True:
    pgbouncer_configured_primary_ip = get_pgbouncer_primary_ip()
    actual_primary_ip = None
    for IP in IPs:
        endpoint = f"http://{IP}:{PORT}/"
        try:
            response = requests.get(endpoint)
            data = json.loads(response.text)
            status = response.status_code
            if status == 200 and data['role'] == 'master':
                actual_primary_ip = IP
        except requests.exceptions.RequestException as e:
            print(f"FAILOVER: {IP}")

    print("ACTUAL PRIMARY IP:", actual_primary_ip)
    print("CONFIGURED PRIMARY IP:", pgbouncer_configured_primary_ip)

    if actual_primary_ip and actual_primary_ip != pgbouncer_configured_primary_ip:
        update_cluster_state(actual_primary_ip)

    send_logging()
    time.sleep(int(os.getenv('CHECK_INTERVAL', 5)))

