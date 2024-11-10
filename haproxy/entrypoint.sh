#!/bin/bash
set -e

confd -backend etcdv3 -node "http://192.168.144.146:2379" -interval 5 -prefix /service/demo57_standby