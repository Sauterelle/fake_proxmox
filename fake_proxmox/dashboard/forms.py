from django import forms
from . import models


class CreateVM(forms.ModelForm):
    class Meta:
        model = models.VirtualMachine
        fields = ["name", "hypervisor", "cpu_usage", "memory_usage"]
