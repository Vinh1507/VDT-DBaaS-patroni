# Generated by Django 5.1.1 on 2024-09-09 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_cluster_customer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='full_name',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='customer',
            name='last_name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='username',
            field=models.CharField(default='hello', max_length=200, unique=True),
        ),
    ]