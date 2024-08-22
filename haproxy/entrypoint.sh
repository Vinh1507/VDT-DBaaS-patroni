#!/bin/bash
set -e

# Start confd to dynamically update the HAProxy config
confd -backend etcdv3 -node http://192.168.144.146:2379 -interval 10 &

# Start HAProxy
exec haproxy -f /etc/haproxy/haproxy.cfg



#!/bin/bash

# readonly PATRONI_SCOPE="${PATRONI_SCOPE:-demo7}"
# PATRONI_NAMESPACE="${PATRONI_NAMESPACE:-/service}"
# readonly PATRONI_NAMESPACE="${PATRONI_NAMESPACE%/}"

# # Start HAProxy in daemon mode
# haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -D

# # Prepare confd command
# set -- confd -prefix="$PATRONI_NAMESPACE/$PATRONI_SCOPE" -interval=10 -backend

# if [ -n "$PATRONI_ZOOKEEPER_HOSTS" ]; then
#     # Wait for Zookeeper to be available
#     while ! /usr/share/zookeeper/bin/zkCli.sh -server "$PATRONI_ZOOKEEPER_HOSTS" ls / > /dev/null 2>&1; do
#         sleep 1
#     done
#     # Add Zookeeper backend
#     set -- "$@" zookeeper -node "$PATRONI_ZOOKEEPER_HOSTS"
# else
#     # Wait for etcd to be available
#     while ! etcdctl member list 2> /dev/null; do
#         sleep 1
#     done
#     # Add etcd backend
#     set -- "$@" etcdv3
#     while IFS='' read -r line; do
#         set -- "$@" -node "$line"
#     done <<< "$(echo "$ETCDCTL_ENDPOINTS" | tr ',' '\n')"
# fi

# # Execute confd with dumb-init
# exec dumb-init "$@"
