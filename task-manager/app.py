# app.py
from flask import Flask, request, jsonify
import dramatiq
import broker  # Import file cấu hình broker
from tasks import initial_cluster, add_node_to_cluster, check_patroni_schedule
import redis
from flask_cors import CORS
import time

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

client = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/trigger-task', methods=['POST'])
def trigger_task():
    # Lấy dữ liệu từ yêu cầu
    data = request.json
    print("[CREATE CLUSTER]: ", data)
    cluster_scope = data.get('cluster_scope')
    node_ips = data.get('node_ips')
    haproxy_ips = data.get('haproxy_ips')
    standby_ips = data.get('standby_ips')
    client.set('node_ips', node_ips)

    print(client.get('node_ips'))
    extra_vars = {
        'PATRONI_SCOPE': cluster_scope,
        'ETCD_PATRONI_CLUSTER_PREFIX': f'/service/{cluster_scope}', 
    }
    array = [node_ips, haproxy_ips, standby_ips]
    limit = ','.join(array)
    initial_cluster.send(extra_vars, limit)

    return jsonify({'message': 'Task has been triggered'}), 200

@app.route('/add-node', methods=['POST'])
def add_node():
    data = request.json
    print("[ADD NODE]: ", data)
    cluster_scope = data.get('cluster_scope')
    node_ip = data.get('node_ip')
    current_nodes = client.get('node_ips').decode("utf-8")

    if node_ip in current_nodes:
        return
    current_nodes = f"{current_nodes},{node_ip}"
    client.set('node_ips', current_nodes)
    extra_vars = {
        'PATRONI_SCOPE': cluster_scope,
    }
    limit = node_ip
    try:
        add_node_to_cluster.send(extra_vars, limit)
    except:
        print('add_node_to_cluster error')

    return jsonify({'message': 'Task ADD NODE has been triggered'}), 200

@app.route('/failover-hook', methods=['POST'])
def failover_hook():
    data = request.json
    print("[failover_hook]: ", data)
    time.sleep(2)
    check_patroni_schedule.send()
    
    return jsonify({'message': 'Task failover_hook has been triggered'}), 200

@app.route('/hello', methods=['POST'])
def hello():
    data = request.json
    print("[hello]: ", data)
    return jsonify({'message': 'hello'}), 200

if __name__ == "__main__":
    app.run(port=8507)
