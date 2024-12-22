from django import forms
from .models import Hypervisor, VirtualMachine

# Formulaire pour ajouter un hyperviseur
class HypervisorForm(forms.ModelForm):
    class Meta:
        model = Hypervisor
        fields = ['name', 'ip_address']

    # Ajout d'un champ pour tester la connexion à l'hyperviseur
    ip_address = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'IP Address'}))
    
# Formulaire pour créer une nouvelle VM
class CreateVMForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    memory = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(attrs={'placeholder': 'Memory (GB)'}))
    vcpu = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(attrs={'placeholder': 'vCPU'}))
    hypervisor = forms.ModelChoiceField(queryset=Hypervisor.objects.all(), required=True, empty_label="Select Hypervisor")
    volume = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Volume Path (e.g., /path/to/volume.qcow2)'}))

    def clean_name(self):
        name = self.cleaned_data['name']
        # Validation pour s'assurer que le nom de la VM n'est pas déjà pris
        if VirtualMachine.objects.filter(name=name).exists():
            raise forms.ValidationError(f"A VM with the name '{name}' already exists.")
        return name

# Formulaire pour supprimer un hyperviseur
class DeleteHypervisorForm(forms.Form):
    confirmation = forms.BooleanField(required=True, label="Are you sure you want to delete this hypervisor?", widget=forms.CheckboxInput())
    
    def clean_confirmation(self):
        confirmation = self.cleaned_data.get('confirmation')
        if not confirmation:
            raise forms.ValidationError("You must confirm the deletion.")
        return confirmation
