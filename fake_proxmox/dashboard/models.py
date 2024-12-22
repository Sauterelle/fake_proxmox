from django.db import models

# Modèle représentant un Hyperviseur
class Hypervisor(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    is_active = models.BooleanField(default=False)  # Etat de la connexion avec l'hyperviseur

    def __str__(self):
        return self.name

# Modèle représentant une VM sur un Hyperviseur
class VirtualMachine(models.Model):
    hypervisor = models.ForeignKey(Hypervisor, related_name="vms", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    uuid = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=50)  # Par exemple: "running", "shut off", etc.
    memory_used_kb = models.IntegerField()
    vcpu_count = models.IntegerField()
    cpu_time_ns = models.BigIntegerField()

    def __str__(self):
        return f"{self.name} ({self.state})"

    class Meta:
        ordering = ['name']

