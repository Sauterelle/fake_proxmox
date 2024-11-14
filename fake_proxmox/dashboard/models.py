from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')])

class VirtualMachine(models.Model):
    name = models.CharField(max_length=100)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='vms')
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    status = models.CharField(max_length=50, choices=[('running', 'Running'), ('stopped', 'Stopped')])
