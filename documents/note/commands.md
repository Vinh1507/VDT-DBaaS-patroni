```
cd ansible
ansible-playbook playbooks/etcd_cluster.yml -K
ansible-playbook playbooks/patroni.yml -K
ansible-playbook playbooks/haproxy.yml -K
ansible-playbook playbooks/standby_cluster.yml -K
```


## Run Task manager, task scheduler, trigger flask API
```
cd task-manager/
source myenv/bin/activate
docker compose up rabbitmq redis
dramatiq tasks
python scheduler.py
python app.py
```


## Run django DBaaS API
```
cd api-cluster-management/
source myenv/bin/activate
docker compose up -d
python manage.py runserver
```

```
confd -backend etcdv3 -node "http://192.168.144.146:2379" -interval 10 -prefix /service/demo57_standby

haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -D -sf $(cat /var/run/haproxy.pid)
```