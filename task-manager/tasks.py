import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import requests
from tabulate import tabulate
from broker import rabbitmq_broker
import os
from dotenv import load_dotenv
import requests
import json
import subprocess
import redis
from datetime import datetime



# Load environment variables from .env file
load_dotenv()
client = redis.Redis(host='localhost', port=6379, db=0)
playbook_path = '/home/vinh/Documents/postgresql-high-availability/ansible/playbooks/patroni_v2.yml'
inventory_path = '/home/vinh/Documents/postgresql-high-availability/ansible/inventory.ini'
remote_user = 'simone'
tags = ["patroni"]
patroni_scope = os.getenv('PATRONI_SCOPE')

@dramatiq.actor
def print_message(message):
    print(f"Received message: {message}")


@dramatiq.actor
def run_ansible_playbook(playbook_path, extra_vars=None, inventory_path=None, remote_user=None, tags=None, limit=None):
    """
    Run an Ansible playbook with optional extra variables.
    
    :param playbook_path: Path to the Ansible playbook file.
    :param extra_vars: Dictionary of extra variables to pass to the playbook.
    :param inventory_path: Path to the inventory file.
    :param remote_user: Remote user to use for the playbook.
    :param tags: Run only playbook match these tags
    :param limit: Run only playbook match this server name
    :return: Dictionary with the result of the execution.
    """
    command = ["ansible-playbook", playbook_path]
    
    if inventory_path:
        command.extend(["-i", inventory_path])

    if extra_vars:
        extra_vars_str = " ".join(f"{key}={value}" for key, value in extra_vars.items())
        command.extend(["-e", extra_vars_str])
    
    if tags:
        tags_str = ",".join(tags)
        command.extend(["-t", tags_str])
    
    if limit:
        command.extend(["--limit", limit])

    if remote_user:
        command.extend(["-u", remote_user])
    
    print(command)
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e}

@dramatiq.actor
def restart_patroni_node(IPs):
    if client.get('is_running_ansible') == b'1':
        return 
    limit = IPs
    client.set('is_running_ansible', '1')   
    vars = {
        'PATRONI_SCOPE': patroni_scope,
    }
    run_ansible_playbook(playbook_path, vars, inventory_path, remote_user, tags, limit)
    client.set('is_running_ansible', '0')

@dramatiq.actor
def check_patroni_schedule():
    print("Starting check...")
    try:
        # Load configurations from environment variables
        IPs = os.getenv('IPS').split(',')
        PORT = int(os.getenv('PORT', 8008))
        failover_IPs = []
        current_time = datetime.now()
        print("[%s]", current_time)
        for IP in IPs:
            endpoint = f"http://{IP}:{PORT}/"
            try:
                response = requests.get(endpoint)
                data = json.loads(response.text)
                if data is None or data['state'] != 'running' :
                    failover_IPs.append(IP)
                    print(f"STOPPED: {IP}")
                else:
                    print(f"RUNNING: {IP}")
            except requests.exceptions.RequestException as e:
                print(f"FAILOVER: {IP}")
                failover_IPs.append(IP)
                
        if len(failover_IPs) > 0:
            restart_patroni_node.send(",".join(failover_IPs))
        print("================================")
    except Exception as e:
        print("Server Error: ", e)

@dramatiq.actor
def initial_cluster(extra_vars = None):
    print("Creating cluster...")
    try:
        run_ansible_playbook(playbook_path, extra_vars, inventory_path, remote_user, tags, None)
    except Exception as e:
        print("Server Error: ", e)