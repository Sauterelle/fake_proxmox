from django.shortcuts import HttpResponseRedirect, get_object_or_404, render
from .utils.kvm_python import get_hypervisor_info_json, createVm
from .models import VirtualMachine
from . import forms
import libvirt


def index(request):
    remote_user = "root"
    remote_hosts = "172.16.136.156"
    conn = libvirt.open("qemu+ssh://" + remote_user + "@" + remote_hosts + "/system")
    hypervisor_info = get_hypervisor_info_json(conn)
    return render(request, "index.html", {"info": hypervisor_info})


def vm_console(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    vnc_host = "localhost"
    vnc_port = "5900"
    no_vnc_url = (
        f"http://{request.get_host()}:6080/vnc.html?host=127.0.0.1&port={vm.vnc_port}"
    )

    return render(request, "vm_console.html", {"no_vnc_url": no_vnc_url, "vm": vm})


def create_vm(request):
    if request.method == "POST":
        form = forms.CreateVM(request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/thanks")
    else:
        form = forms.CreateVM()
    return render(request, "vm_new.html", {"vm_form": form})

    # if request.method == "POST":
    #     vm_name = request.POST.get("vm_name")
    #     hypervisor = request.POST.get("hypervisor")
    #     vm_memory = request.POST.get("vm_memory")
    #     vm_cpu = request.POST.get("vm_cpu")
    #     try:
    #         createVm(hypervisor,vm_name,)
    #
    # else:
    #     form = forms.CreateVM()
    # return render(request, "post/vm_new.html", {"form": form})
