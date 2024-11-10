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
playbook_path = '/home/vinh/Documents/postgresql-high-availability/ansible/playbooks/patroni.yml'
inventory_path = '/home/vinh/Documents/postgresql-high-availability/ansible/inventory.ini'
remote_user = 'simone'
tags = ["patroni"]
patroni_scope = os.getenv('PATRONI_SCOPE')
STANDBY_IP = '192.168.144.149'
STANDBY_PORT = 8008

@dramatiq.actor
def print_message(message):
    print(f"Received message: {message}")


@dramatiq.actor
def run_ansible_playbook(playbook_path, extra_vars=None, inventory_path=None, remote_user=None, tags=None, limit=None):
    if client.get('creating_cluster') == b'1':
        print("I'm creating cluster")
        return
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
        for key, value in extra_vars.items():
            command.extend(["-e", f"{key}={value}"])        
    
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
def restart_patroni_node(IPs, cluster_scope = None):
    if cluster_scope is None:
        return
    if client.get('is_running_ansible') == b'1':
        return 
    limit = IPs
    client.set('is_running_ansible', '1')   
    vars = {
        'PATRONI_SCOPE': cluster_scope,
    }
    
    run_ansible_playbook(playbook_path, vars, inventory_path, remote_user, tags, limit)

@dramatiq.actor
def check_patroni_schedule():
    print("Checking status...", datetime.now())
    try:
        # Load configurations from environment variables
        IPs = client.get('node_ips').decode('utf-8').split(',')
        print("IPs", IPs)
        PORT = int(os.getenv('PORT', 8008))
        failover_IPs = []
        print("[TIME]", )
        cluster_scope = None
        for IP in IPs:
            endpoint = f"http://{IP}:{PORT}/"
            try:
                response = requests.get(endpoint)
                data = json.loads(response.text)
                if data is None or data['state'] != 'running' :
                    failover_IPs.append(IP)
                    print(f"STOPPED: {IP}")
                else:
                    cluster_scope = data['patroni']['scope']
                    print(f"RUNNING: {IP}")
            except requests.exceptions.RequestException as e:
                print(f"FAILOVER: {IP}")
                failover_IPs.append(IP)

        if len(failover_IPs) == len(IPs):
            switch_to_standby_cluster()
        elif len(failover_IPs) > 0:
            restart_patroni_node.send(",".join(failover_IPs), cluster_scope)
            client.set('is_running_ansible', '0')
        else:
            client.set('is_running_ansible', '0')
        print("================================")
    except Exception as e:
        print("Server Error: ", e)

@dramatiq.actor
def initial_cluster(extra_vars = None, limit = None):
    print(f"Creating {extra_vars['PATRONI_SCOPE']} cluster...")
    create_cluster_playbook_path = '/home/vinh/Documents/postgresql-high-availability/ansible/playbooks/create_cluster.yml'
    try:
        run_ansible_playbook(create_cluster_playbook_path, extra_vars, inventory_path, remote_user, None, limit)
        client.set('creating_cluster', '1')
    except Exception as e:
        print("Server Error: ", e)
    client.set('creating_cluster', '0')

@dramatiq.actor
def add_node_to_cluster(extra_vars = None, limit = None):
    print("Adding node...")
    add_node_playbook_path = '/home/vinh/Documents/postgresql-high-availability/ansible/playbooks/patroni.yml'
    try:
        run_ansible_playbook(add_node_playbook_path, extra_vars, inventory_path, remote_user, tags, limit)
    except Exception as e:
        print("Server Error: ", e)

def switch_to_standby_cluster():
    # client.set('is_running_standby_ansible', '0') 
    # if client.get('is_running_standby_ansible') == b'1':
    #     return 
    # client.set('is_running_standby_ansible', '1')  

    info_endpoint = f"http://{STANDBY_IP}:{STANDBY_PORT}/"
    info_response = requests.get(info_endpoint)
    info_data = json.loads(info_response.text)
    cluster_scope = f"/service/{info_data['patroni']['scope']}"
    print(cluster_scope)
    # redirect_proxy_to_new_cluster(cluster_scope)
    if info_data is None or info_data['state'] != 'running' or not info_data['role'].startswith("standby"):
        return
    
    print('STARTING SWITCH TO STANDBY CLUSTER')
    client.set('is_running_standby_ansible', '1')  
    try:
        
        config_endpoint = f"http://{STANDBY_IP}:{STANDBY_PORT}/config"
        print(config_endpoint)
        response = requests.get(config_endpoint)
        data = json.loads(response.text)
        if 'standby_cluster' in data:
            del data['standby_cluster']
            response = requests.put(config_endpoint, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                print('Cập nhật thành công!')
                print('Response:', response.json())  # In ra kết quả dưới dạng JSON

                redirect_proxy_to_new_cluster(cluster_scope)
                client.set('node_ips', STANDBY_IP)
                # client.set('is_running_standby_ansible', '2')  
            else:
                print(f'Lỗi: {response.status_code}')
                print('Nội dung phản hồi:', response.text)
            
            
    except Exception as e:
        print("Server Error: ", e)
    # finally:
        # client.set('is_running_standby_ansible', '0')  

def redirect_proxy_to_new_cluster(cluster_scope):
    vars = {
        'ETCD_PATRONI_CLUSTER_PREFIX': cluster_scope
    }
    haproxy_playbook_path = '/home/vinh/Documents/postgresql-high-availability/ansible/playbooks/haproxy.yml'
    run_ansible_playbook(haproxy_playbook_path, vars, inventory_path, remote_user, None, None)
    
@dramatiq.actor
def promote_standby_cluster(extra_vars = None):
    try:
        switch_to_standby_cluster()
    except Exception as e:
        print("Server Error: ", e)