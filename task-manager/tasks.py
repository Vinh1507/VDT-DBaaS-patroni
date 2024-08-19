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


# Load environment variables from .env file
load_dotenv()

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
def restart_patroni_node(IP):
    playbook_path = '/home/vinh/Documents/postgresql-high-availability/ansible/playbooks/patroni_cluster.yml'
    inventory_path = '/home/vinh/Documents/postgresql-high-availability/ansible/inventory.ini'
    remote_user = 'simone'
    tags = ["patroni"]
    limit = IP
    run_ansible_playbook(playbook_path, None, inventory_path, remote_user, tags, limit)

@dramatiq.actor
def check_patroni_schedule():
    try:
        # Load configurations from environment variables
        IPs = os.getenv('IPS').split(',')
        PORT = int(os.getenv('PORT', 8008))

        for IP in IPs:
            endpoint = f"http://{IP}:{PORT}/"
            try:
                response = requests.get(endpoint)
                data = json.loads(response.text)
                if data is None or data['state'] == 'stopped' :
                    restart_patroni_node.send(IP)
                    print(f"STOPPED: {IP}")
                else:
                    print(f"RUNNING: {IP}")
            except requests.exceptions.RequestException as e:
                print(f"FAILOVER: {IP}")
                restart_patroni_node.send(IP)
        print("================================")
    except Exception as e:
        print("Server Error: ", e)