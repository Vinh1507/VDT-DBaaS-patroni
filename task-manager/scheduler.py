import requests
import time
import json
import re

# Danh sách các endpoint
IPs = [
    '192.168.144.133',
    '192.168.144.135',
    '192.168.144.136',
]
PORT = 8008
CONFIG_FILE_PATH = './pgbouncer.ini'


def get_pgbouncer_db_config (): 
    with open(CONFIG_FILE_PATH, 'r') as file:
        text = file.read()

    # Regular expression to extract the content between the markers
    match = re.search(r';; \[config cluster: begin\](.*?);; \[config cluster: end\]', text, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        return extracted_text
    else:
        return None
    
def get_pgbouncer_primary_ip ():
    connection_string = get_pgbouncer_db_config()

    if connection_string is None:
        return None
    
    host_match = re.search(r'host=(\d+\.\d+\.\d+\.\d+)', connection_string)

    if host_match:
        host_value = host_match.group(1)
        return host_value
    else:
        return None

while True:
    pgbouncer_configered_primary_ip = get_pgbouncer_primary_ip()
    actual_primary_ip = None
    for IP in IPs:
        endpoint = f"http://{IP}:{PORT}/"
        try:
            response = requests.get(endpoint)
            data = json.loads(response.text)
            status = response.status_code
            if status == 200 and data['role'] == 'master':
                actual_primary_ip = IP
            # print(f"Response from {endpoint}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"FAILOVER: {IP}")
        
    print("ACTUAL PRIMARY IP:", actual_primary_ip)
    print("CONFIGERED PRIMARY IP:", pgbouncer_configered_primary_ip)
    time.sleep(5)
