import libvirt
import json

"""
TODO à faire
"""


def domains_to_xml(conn):
    list_domains = conn.listAllDomains()
    with open("vms_info.xml", "w") as file:
        for domain in list_domains:
            file.write(domain.XMLDesc())


def shutdown_vm(domain):
    if domain.isActive():
        domain.destroy()
    else:
        print("domain is already innactive")


def start_vm(domain):
    state = domain.state()
    print(state)


def get_vm_info(domain):
    info = domain.info()
    vm_info = {
        "name": domain.name(),
        "uuid": domain.UUIDString(),
        "state": info[0],
        "max_memory_kb": info[1],
        "memory_used_kb": info[2],
        "vcpu_count": info[3],
        "cpu_time_ns": info[4],
    }

    return vm_info


def get_hypervisor_info_json(conn):
    info = conn.getInfo()
    hypervisor_info = {
        "uri": conn.getURI(),
        "hostname": conn.getHostname(),
        "cpu_model": info[0],
        "memory_size_mb": info[1],
        "cpu_count": info[2],
        "cpu_frequency_mhz": info[3],
        "numa_nodes": info[4],
        "cpu_sockets_per_node": info[5],
        "cores_per_socket": info[6],
        "threads_per_core": info[7],
        "domains": [],
    }

    for domain_id in conn.listDomainsID():
        domain = conn.lookupByID(domain_id)
        hypervisor_info["domains"].append(get_vm_info(domain))

    for domain_name in conn.listDefinedDomains():
        domain = conn.lookupByName(domain_name)
        hypervisor_info["domains"].append(get_vm_info(domain))

    hypervisor_info_json = json.dumps(hypervisor_info, indent=4)

    return hypervisor_info_json


remote_user = "root"
remote_hosts = "172.16.136.156"

conn = libvirt.open("qemu+ssh://" + remote_user + "@" + remote_hosts + "/system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")


print(get_hypervisor_info_json(conn))

# print_active_domains(conn)
# print_all_domains(conn)
# nodeinfo = conn.getInfo()


conn.close()
