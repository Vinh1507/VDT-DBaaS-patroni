# Báo cáo tiến độ #6

## Mục tiêu:

- Triển khai cluster Patroni và các service liên quan trên Kubernetes
    + Thử nghiệm phiên bản deploy từng thành phần
    + Thử nghiệm phiên bản sử dụng Operator
- Thử nghiệm các tính năng cũ trên môi trường Kubernetes: 
    + Tự động chuyển đổi failover/switchover
    + Thêm/bớt node không gây gián đoạn

- Triển khai standby cluster cho phiên bản dành cho VMs
    + Thử nghiệm chủ động switchover sang DC standby
    + Thử nghiệm failover cấp độ DC primary

## Triển khai cluster Patroni và các service liên quan trên Kubernetes
### 1. Thử nghiệm phiên bản deploy từng thành phần

[Manifest triển khai cụm patroni](https://github.com/patroni/patroni/tree/master/kubernetes)

```
kubectl get pods -L role

# Kết quả:
patronidemo-0                            1/1     Running            1 (107m ago)   11h   replica
patronidemo-1                            1/1     Running            1 (107m ago)   11h   replica
patronidemo-2                            1/1     Running            1 (107m ago)   11h   primary
```

```
kubectl get svc

# Kết quả:
patronidemo                 ClusterIP   10.98.32.181    <none>        5432/TCP                                       16h
patronidemo-config          ClusterIP   None            <none>        <none>                                         16h
patronidemo-repl            ClusterIP   10.100.187.54   <none>        5432/TCP                                       16h

```


haproxy.yml triển khai NodePort Haproxy.
```yml
    listen primary
      bind *:5000
      server patroni-0 patronidemo:5432 check
      
    listen replicas
      bind *:5001
      server patroni-repl patronidemo-repl:5432 check
```

Sử dụng patronidemo (service cho role primary), tương tự sử dụng service patronidemo-repl (service cho role replica)


Note: Phiên bản này gồm 3 pod Patroni và 1 pod Haproxy


### 2. Phiên bản sử dụng Operator

#### Ref: https://github.com/zalando/postgres-operator/blob/master/docs/quickstart.md

#### Manual deployment setup on Kubernetes

Chú ý, cần cấu hình tự động tạo PV khi có yêu cầu tạo PVC

```bash
# First, clone the repository and change to the directory
git clone https://github.com/zalando/postgres-operator.git
cd postgres-operator

# apply the manifests in the following order
kubectl create -f manifests/configmap.yaml  # configuration
kubectl create -f manifests/operator-service-account-rbac.yaml  # identity and permissions
kubectl create -f manifests/postgres-operator.yaml  # deployment
kubectl create -f manifests/api-service.yaml  # operator API to be used by UI
```


Check if Postgres Operator is running

```bash
kubectl get pod -l name=postgres-operator

NAME                                 READY   STATUS    RESTARTS        AGE
postgres-operator-5bcb7b8d94-f7f76   1/1     Running   2 (5h24m ago)   27h
```

Create a Postgres cluster
```bash
kubectl create -f manifests/minimal-postgres-manifest.yaml
```

```shell
# check the deployed cluster
kubectl get postgresql

NAME                   TEAM   VERSION   PODS   VOLUME   CPU-REQUEST   MEMORY-REQUEST   AGE     STATUS
acid-minimal-cluster   acid   16        2      1Gi                                     3h56m   Running

# check created database pods
kubectl get pods -l application=spilo -L spilo-role

NAME                     READY   STATUS    RESTARTS   AGE     SPILO-ROLE
acid-minimal-cluster-0   1/1     Running   0          3h27m   master
acid-minimal-cluster-1   1/1     Running   0          3h23m   replica

# check created service resources
kubectl get svc -l application=spilo -L spilo-role

NAME                          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE     SPILO-ROLE
acid-minimal-cluster          ClusterIP   10.101.63.234   <none>        5432/TCP   3h57m   master
acid-minimal-cluster-config   ClusterIP   None            <none>        <none>     3h23m   
acid-minimal-cluster-repl     ClusterIP   10.104.19.21    <none>        5432/TCP   3h57m   replica
```

#### Triển khai NodePort Haproxy

[Manifest haproxy](../k8s/haproxy.yml)

## Triển khai standby cluster cho phiên bản dành cho VMs

#### Ref: 
- [Patroni Standby Cluster Docs](https://patroni.readthedocs.io/en/latest/standby_cluster.html)


Cấu hình cho Standby Cluster
- Standby Cluster sẽ dùng 1 cụm etcd khác hoàn toàn với cụm etcd đanh cho Primary Cluster

```ini
# File inventory.ini
[patroni_standby]
192.168.144.149 ansible_host=192.168.144.149 name=standby-node1

[etcd_standby]
etcd-standby1 ansible_host=192.168.144.133 name=etcd-standby1
```

Cấu hình bootstrap cho cụm Standby cần bổ sung:
Trong đó cần trỏ tới Primary Node Endpoint, sử dụng Haproxy để truy cập tới Primary Node Endpoint tự động

```yaml
dcs:
  standby_cluster:
    host: 192.168.144.1 # haproxy IP
    port: 7001 # haproxy port
    create_replica_methods:
    - basebackup
```

Tại node standby-node1 (trong cluster standby), thực hiện list các node
```shell
patronictl list

# Kết quả:
+ Cluster: demo05_standby (7416207338305745004) ---+-----------+----+-----------+
| Member        | Host            | Role           | State     | TL | Lag in MB |
+---------------+-----------------+----------------+-----------+----+-----------+
| standby-node1 | 192.168.144.149 | Standby Leader | streaming |  2 |           |
+---------------+-----------------+----------------+-----------+----+-----------+
```

## Thử nghiệm failover 1 node trong Primary Cluster, kiểm tra streaming replication tới Standby node

Tại Primary Cluster
```
patronictl failover
Current cluster topology
+ Cluster: demo02 (7416207338305745004) ---------+----+-----------+
| Member | Host            | Role    | State     | TL | Lag in MB |
+--------+-----------------+---------+-----------+----+-----------+
| node1  | 192.168.144.133 | Replica | streaming |  1 |         0 |
| node2  | 192.168.144.135 | Leader  | running   |  1 |           |
| node3  | 192.168.144.136 | Replica | streaming |  1 |         0 |
+--------+-----------------+---------+-----------+----+-----------+
Candidate ['node1', 'node3'] []: node1
Are you sure you want to failover cluster demo02, demoting current leader node2? [y/N]: y
2024-09-19 04:38:12.40028 Successfully failed over to "node1"
```

Tại Node1, thêm bản ghi và kiểm tra xem Standby Node 1 có nhận được bản ghi mới hay không

```
insert into tmp values (2, now());
```

Kiểm tra tại Standby Node 1 

```
postgres=# select * from tmp;
 id |            time            
----+----------------------------
  1 | 2024-09-19 04:36:15.186035
  2 | 2024-09-19 04:39:51.739119
```

==> Replicate bình thường

## Thử nghiệm promote standby cluster thành 1 primary cluster

```bash
patronictl list
+ Cluster: demo05_standby (7416207338305745004) ---+---------+----+-----------+
| Member        | Host            | Role           | State   | TL | Lag in MB |
+---------------+-----------------+----------------+---------+----+-----------+
| standby-node1 | 192.168.144.149 | Standby Leader | running |  3 |           |
+---------------+-----------------+----------------+---------+----+-----------+


patronictl edit-config

# Xóa hết section về standby_cluster, và lưu thay đổi
--- 
+++ 
@@ -10,9 +10,9 @@
   - host all all all md5
   use_pg_rewind: true
 retry_timeout: 10
-standby_cluster:
+  #standby_cluster:
-  create_replica_methods:
+  # create_replica_methods:
-  - basebackup
+  # - basebackup
-  host: 192.168.144.1
+  # host: 192.168.144.1
-  port: 7001
+  # port: 7001
 ttl: 30

Apply these changes? [y/N]: y
Configuration changed
postgres@standby-node1:~$ patronictl list
+ Cluster: demo05_standby (7416207338305745004) -----+----+-----------+
| Member        | Host            | Role   | State   | TL | Lag in MB |
+---------------+-----------------+--------+---------+----+-----------+
| standby-node1 | 192.168.144.149 | Leader | running |  4 |           |
+---------------+-----------------+--------+---------+----+-----------+
```

Sau đó, client có thể kết nối read/write tới cụm này