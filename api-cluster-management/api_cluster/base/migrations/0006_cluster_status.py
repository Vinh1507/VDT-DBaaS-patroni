# Generated by Django 5.1.1 on 2024-09-09 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_remove_cluster_node_list_node_alter_backup_node_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
