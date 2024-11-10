from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import BaseUser, Cluster
from .serializers import BaseUserSerializer, ClusterSerializer
import requests
import etcd3
from django.http import JsonResponse
import json

# Connect to the etcd server
etcd = etcd3.client(
    host='192.168.144.146',  # Replace with your etcd host
    port=2379,              # Replace with your etcd port
)  # Defaults to localhost:2379

# Create a new BaseUser
@api_view(['POST'])
def create_user(request):
    serializer = BaseUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve a BaseUser by ID
@api_view(['GET'])
def retrieve_user(request, pk):
    user = get_object_or_404(BaseUser, pk=pk)
    serializer = BaseUserSerializer(user)
    return Response(serializer.data)

# Update a BaseUser by ID (PUT)
@api_view(['PUT'])
def update_user(request, pk):
    user = get_object_or_404(BaseUser, pk=pk)
    serializer = BaseUserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete a BaseUser by ID
@api_view(['DELETE'])
def delete_user(request, pk):
    user = get_object_or_404(BaseUser, pk=pk)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Create a new Cluster
@api_view(['POST'])
def create_cluster(request):
    data = json.loads(request.body)
    node_ips = data.get('node_ips')
    haproxy_ips = data.get('haproxy_ips')
    standby_ips = data.get('standby_ips')
    cluster_scope = data.get('cluster_scope')
    body = {
        'cluster_scope': cluster_scope,
        'node_ips': node_ips,
        'haproxy_ips': haproxy_ips,
        'standby_ips': standby_ips,
    }
    try:
        url = 'http://localhost:8507/trigger-task'
        response = requests.post(url, json=body)
        # Kiểm tra phản hồi
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        return Response(body, status=status.HTTP_201_CREATED)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

# Retrieve a Cluster by ID
@api_view(['GET'])
def retrieve_cluster(request, pk):
    cluster = get_object_or_404(Cluster, pk=pk)
    serializer = ClusterSerializer(cluster)

    prefix = '/service/' + serializer.data['cluster_scope']
    cluster_etcd_data = {}
    for value, metadata in etcd.get_prefix(prefix):
        first = metadata.key.decode("utf-8")
        second = value.decode("utf-8")
        try:
            cluster_etcd_data[first] = json.loads(second)
        except Exception:
            cluster_etcd_data[first] = (second)
        print(f'Key: {metadata.key.decode("utf-8")}, Value: {value.decode("utf-8")}')

    data = {
        'cluster_etcd_data': cluster_etcd_data,
        'cluster_info': serializer.data
    }
    return JsonResponse(data)

# Update a Cluster by ID (PUT)
@api_view(['PUT'])
def update_cluster(request, pk):
    cluster = get_object_or_404(Cluster, pk=pk)
    serializer = ClusterSerializer(cluster, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete a Cluster by ID
@api_view(['DELETE'])
def delete_cluster(request, pk):
    cluster = get_object_or_404(Cluster, pk=pk)
    cluster.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Failover a Cluster by ID
@api_view(['POST'])
def failover(request):
    data = json.loads(request.body)
    candidate = data.get('candidate')
    cluster_scope = data.get('cluster_scope')
    print(candidate)
    prefix = '/service/' + cluster_scope + '/members/' + candidate 
    patroni_members = etcd.get_prefix(prefix)
    candidate_member = next(patroni_members, None)
    if patroni_members:
        # try:
            member_value_json = candidate_member[0].decode("utf-8")
            member_value = json.loads(member_value_json)
            if member_value['state'] == 'running':
                failover_url = member_value['api_url'].replace('/patroni', '/failover')
                failover_body = {
                    'candidate': candidate,
                }
                failover_response = requests.post(failover_url, json=failover_body)
                return Response(failover_response)
        # except:
        #     print("Something went wrong") 
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def switchover(request):
    data = json.loads(request.body)
    candidate = data.get('candidate')
    cluster_scope = data.get('cluster_scope')
    print(candidate)
    candidate_prefix = '/service/' + cluster_scope + '/members/' + candidate 
    patroni_members = etcd.get_prefix(candidate_prefix)
    candidate_member = next(patroni_members, None)
    if patroni_members:
        # try:
            member_value_json = candidate_member[0].decode("utf-8")
            member_value = json.loads(member_value_json)
            failover_url = member_value['api_url'].replace('/patroni', '/failover')
            leader_key = '/service/' + cluster_scope + '/leader'
            leader = etcd.get(leader_key)[0].decode("utf-8")
            print(leader)
            failover_body = {
                'leader': leader,
                'candidate': candidate,
            }
            failover_response = requests.post(failover_url, json=failover_body)
            return Response(("Failover thành công"))
        # except:
        #     print("Something went wrong") 
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_node(request):
    data = json.loads(request.body)
    node_ip = data.get('node_ip')
    cluster_scope = data.get('cluster_scope')

    try:
        add_note_url = 'http://localhost:8507/add-node'
        body = {
            'cluster_scope': cluster_scope,
            'node_ip': node_ip,
        }
        add_node_response = requests.post(add_note_url, json=body)
        return Response(json.loads(add_node_response))
    except:
        print("Some error")
    return Response(status=status.HTTP_200_OK)