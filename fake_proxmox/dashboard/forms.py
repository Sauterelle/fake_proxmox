from django import forms
from . import models


class CreateVM(forms.ModelForm):
    class Meta:
        model = models.VirtualMachine
        fields = ["name", "hypervisor", "cpu_usage", "memory_usage"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter VM name"}
            ),
            "hypervisor": forms.Select(attrs={"class": "form-control"}),
            "cpu_usage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "CPU usage (%)",
                }
            ),
            "memory_usage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Memory usage (MB)",
                }
            ),
        }
        labels = {
            "name": "Virtual Machine Name",
            "hypervisor": "Select Hypervisor",
            "cpu_usage": "CPU Usage (%)",
            "memory_usage": "Memory Usage (MB)",
        }
