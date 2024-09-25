#!/bin/bash
set -e

# Start confd to dynamically update the HAProxy config
confd -backend etcdv3 -nodes "http://192.168.144.146:2379" -interval 10

# Start HAProxy
# exec haproxy -f /etc/haproxy/haproxy.cfg