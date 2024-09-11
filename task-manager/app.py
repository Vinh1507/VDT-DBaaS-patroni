# app.py
from flask import Flask, request, jsonify
import dramatiq
import broker  # Import file cấu hình broker
from tasks import initial_cluster

app = Flask(__name__)

@app.route('/trigger-task', methods=['POST'])
def trigger_task():
    # Lấy dữ liệu từ yêu cầu
    data = request.json
    print(">>> flask: ", data)
    cluster_scope = data.get('cluster_scope')
    # param2 = data.get('param2')

    extra_vars = {
        'PATRONI_SCOPE': cluster_scope,
    }
    # Gửi task vào hàng đợi
    initial_cluster.send(extra_vars)

    return jsonify({'message': 'Task has been triggered'}), 200

if __name__ == "__main__":
    app.run(debug=True)
