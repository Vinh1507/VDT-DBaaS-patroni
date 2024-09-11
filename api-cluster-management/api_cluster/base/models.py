from django.db import models

# Create your models here.

from django.db import models

# Create your models here.

class BaseUser(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=20, null=True)
    username = models.CharField(default='hello', max_length=200, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    birthday = models.CharField(max_length=20, null=True, blank=True)
    class Meta:
        db_table = 'base_user'

    def __str__(self) -> str:
        return self.first_name

class Cluster(models.Model):
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    cluster_namespace = models.CharField(max_length=255, null=True, blank=True)
    haproxy_info = models.TextField(null=True)
    cluster_scope = models.CharField(max_length=255, unique=True)
    config = models.JSONField()  # Cấu hình lưu dưới dạng JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.cluster_namespace}/{self.cluster_scope}' 

class Node(models.Model):
    name = models.CharField(max_length=255)  # Tên hoặc ID của node
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Địa chỉ IP của node
    cluster = models.ForeignKey('Cluster', on_delete=models.CASCADE, related_name='nodes')
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return self.name
    
class FailoverHistory(models.Model):
    EVENT_TYPE_CHOICES = [
        ('failover', 'Failover'),
        ('switchover', 'Switchover'),
    ]

    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='failover_history')
    old_leader = models.ForeignKey('Node', on_delete=models.SET_NULL, related_name='old_leader_failovers', null=True, blank=True)
    new_leader = models.ForeignKey('Node', on_delete=models.SET_NULL, related_name='new_leader_failovers', null=True, blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    initiated_by = models.CharField(max_length=255)  # Người hoặc hệ thống khởi động
    reason = models.TextField(blank=True, null=True)  # Lý do failover
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event_type} from {self.old_leader} to {self.new_leader}'

class Backup(models.Model):
    BACKUP_TYPE_CHOICES = [
        ('full', 'Full'),
        ('incremental', 'Incremental'),
        ('pitr', 'PITR'),
    ]

    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='backups')
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='backups') 
    backup_type = models.CharField(max_length=12, choices=BACKUP_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    backup_status = models.CharField(max_length=255)
    backup_size = models.BigIntegerField()
    backup_location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Backup ({self.backup_type}) for {self.node} at {self.start_time}'
