from django.db import models
from libvirt import libvirtError
from .utils.kvm_python import connect_hypervisor


class Hypervisor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    uri = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def test_connection(self):
        try:
            conn = connect_hypervisor(str(self.uri))
            if conn:
                conn.close()
                return True
        except libvirtError:
            return False
        return False


class VirtualMachine(models.Model):
    name = models.CharField(max_length=100)
    hypervisor = models.ForeignKey(
        Hypervisor,
        on_delete=models.CASCADE,
        related_name="vms",
        default=1,
    )
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    status = models.CharField(
        max_length=50, choices=[("running", "Running"), ("stopped", "Stopped")]
    )
