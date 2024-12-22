import libvirt
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Hypervisor, VirtualMachine
from .forms import HypervisorForm, CreateVMForm, DeleteHypervisorForm
from .utils.kvm_python import createVm, get_vm_info, get_hypervisor_info_json, destroyVm, startVm

# Fonction de connexion centralisée
def connexion(hypervisor=None):
    """
    Fonction qui établit une connexion à l'hyperviseur.
    Si `hypervisor` est fourni, on se connecte à l'hyperviseur distant via SSH, sinon on se connecte localement.
    """
    try:
        # if hypervisor:
        #     # Connexion distante via SSH
        #     conn = libvirt.open(f'qemu+ssh://root@{hypervisor.ip_address}/system')
        # else:
            # Connexion locale
        conn = libvirt.open(f'qemu:///system')
        return conn
    except libvirt.libvirtError as e:
        return None  

# Affiche la liste des hyperviseurs
def hypervisor_list(request):
    hypervisors = Hypervisor.objects.all()
    return render(request, 'hypervisor_list.html', {'hypervisors': hypervisors})

# Formulaire pour ajouter un hyperviseur
def add_hypervisor(request):
    if request.method == 'POST':
        form = HypervisorForm(request.POST)
        if form.is_valid():
            ip_address = form.cleaned_data['ip_address']
            name = form.cleaned_data['name']
            try:
               
                conn = connexion(hypervisor=form.instance) 
                if conn:
                    conn.close()
                    form.save()  
                    return redirect('hypervisor_list')
                else:
                    return HttpResponse("Échec de la connexion à l'hyperviseur.", status=400)

            except libvirt.libvirtError as e:
                return HttpResponse(f"Erreur de connexion: {str(e)}", status=400)
    else:
        form = HypervisorForm()

    return render(request, 'add_hypervisor.html', {'form': form})

# Supprimer un hyperviseur après confirmation
def delete_hypervisor(request, hypervisor_id):
    hypervisor = get_object_or_404(Hypervisor, id=hypervisor_id)

    if request.method == 'POST':
        form = DeleteHypervisorForm(request.POST)
        if form.is_valid():
            hypervisor.delete()
            return redirect('hypervisor_list')
    else:
        form = DeleteHypervisorForm()

    return render(request, 'delete_hypervisor.html', {'form': form, 'hypervisor': hypervisor})


def vm_list(request, hypervisor_id):
    # Récupérer l'hyperviseur en question
    hypervisor = get_object_or_404(Hypervisor, id=hypervisor_id)
    
    # Récupérer toutes les VMs associées à cet hyperviseur
    vms = VirtualMachine.objects.filter(hypervisor=hypervisor)
    
    # Rendre la page avec la liste des VMs
    return render(request, 'vm_list.html', {'hypervisor': hypervisor, 'vms': vms})


# Créer une nouvelle VM
def create_vm(request):
    if request.method == 'POST':
        form = CreateVMForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            memory = form.cleaned_data['memory']
            vcpu = form.cleaned_data['vcpu']
            hypervisor = form.cleaned_data['hypervisor']
            volume = form.cleaned_data['volume']
            try:
                conn = connexion(hypervisor=hypervisor)
                if not conn:
                    return HttpResponse("Échec de la connexion à l'hyperviseur.", status=400)

                createVm(conn, name, volume, vcpu, memory)
                conn.close()
                return redirect('vm_list', hypervisor_id=hypervisor.id)
            except libvirt.libvirtError:
                return HttpResponse("Échec de la création de la VM.", status=400)
    else:
        form = CreateVMForm()

    return render(request, 'create_vm.html', {'form': form})

# Affiche les détails d'une VM spécifique
def vm_detail(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    try:
        conn = connexion(hypervisor=vm.hypervisor)
        if not conn:
            return HttpResponse("Échec de la connexion à l'hyperviseur.", status=400)

        domain = conn.lookupByName(vm.name)
        vm_info = get_vm_info(domain)
        conn.close()
    except libvirt.libvirtError:
        return HttpResponse("Erreur lors de la récupération des informations de la VM.", status=400)

    return render(request, 'vm_detail.html', {'vm': vm_info})

# Démarre une VM
def start_vm(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    try:
        conn = connexion(hypervisor=vm.hypervisor)
        if not conn:
            return HttpResponse("Échec de la connexion à l'hyperviseur.", status=400)

        domain = conn.lookupByName(vm.name)
        startVm(domain)
        conn.close()
    except libvirt.libvirtError:
        return HttpResponse("Échec du démarrage de la VM.", status=400)

    return redirect('vm_detail', vm_id=vm.id)

# Arrête une VM
def stop_vm(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    try:
        conn = connexion(hypervisor=vm.hypervisor)
        if not conn:
            return HttpResponse("Échec de la connexion à l'hyperviseur.", status=400)

        domain = conn.lookupByName(vm.name)
        destroyVm(domain)
        conn.close()
    except libvirt.libvirtError:
        return HttpResponse("Échec de l'arrêt de la VM.", status=400)

    return redirect('vm_detail', vm_id=vm.id)

# Suppression d'une VM
def delete_vm(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)

    try:
        conn = connexion(hypervisor=vm.hypervisor)
        if not conn:
            return HttpResponse("Échec de la connexion à l'hyperviseur.", status=400)

        domain = conn.lookupByName(vm.name)
        domain.undefine() 
        conn.close()
        vm.delete()  
    except libvirt.libvirtError:
        return HttpResponse("Échec de la suppression de la VM.", status=400)

    return redirect('vm_list', hypervisor_id=vm.hypervisor.id)

# Ajout de la vue add_vm pour créer une nouvelle VM
def add_vm(request, hypervisor_id):
    hypervisor = get_object_or_404(Hypervisor, id=hypervisor_id)

    if request.method == 'POST':
        form = CreateVMForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            memory = form.cleaned_data['memory']
            vcpu = form.cleaned_data['vcpu']
            volume = form.cleaned_data['volume']

            try:

                conn = connexion(hypervisor=hypervisor)
                if not conn:
                    return HttpResponse("Échec de la connexion à l'hyperviseur.", status=400)

                createVm(conn, name, volume, vcpu, memory)
                conn.close()
                return redirect('vm_list', hypervisor_id=hypervisor.id)
            except libvirt.libvirtError:
                return HttpResponse("Échec de la création de la VM.", status=400)
    else:
        form = CreateVMForm()

    return render(request, 'create_vm.html', {'form': form, 'hypervisor': hypervisor})
