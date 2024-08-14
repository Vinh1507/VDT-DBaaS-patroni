from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

def run_ansible_playbook(playbook_path, extra_vars=None, inventory_path=None, remote_user=None):
    """
    Run an Ansible playbook with optional extra variables.
    
    :param playbook_path: Path to the Ansible playbook file.
    :param extra_vars: Dictionary of extra variables to pass to the playbook.
    :param inventory_path: Path to the inventory file.
    :param remote_user: Remote user to use for the playbook.
    :return: Dictionary with the result of the execution.
    """
    command = ["ansible-playbook", playbook_path]
    
    if inventory_path:
        command.extend(["-i", inventory_path])

    if extra_vars:
        extra_vars_str = " ".join(f"{key}={value}" for key, value in extra_vars.items())
        command.extend(["-e", extra_vars_str])
    
    if remote_user:
        command.extend(["-u", remote_user])
    
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}

@app.route('/run_playbook', methods=['POST'])
def run_playbook():
    playbook_path = '/home/vinh/Documents/postgresql-high-availability/ansible/playbooks/patroni_manage.yml'
    inventory_path = '/home/vinh/Documents/postgresql-high-availability/ansible/inventory.ini'
    remote_user = 'simone'
    extra_vars = {
        'patroni_primary_host': '192.168.144.130'
    }    
    # playbook_path = data.get('playbook_path')
    # extra_vars = data.get('extra_vars', {})
    # inventory_path = data.get('inventory_path')
    # remote_user = data.get('remote_user')

    if not playbook_path:
        return jsonify({"error": "playbook_path is required"}), 400

    result = run_ansible_playbook(playbook_path, extra_vars, inventory_path, remote_user)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500

if __name__ == '__main__':
    app.run(debug=True)
