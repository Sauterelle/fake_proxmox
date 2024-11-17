import libvirt

"""
TODO à faire

- Ajouter une connexion QUEMU/KVM

  ---------Network---------
    Crée un nouveau réseau  

  ---------VM---------
  migrer vm 
  demarrer
  suspendre
  eteindre
  redémarer
  cloners
  supprimer
  snapshot
  ---------Gestion disque---------
  creer un pool 
  Cree un volume qcow2 : fait (par défaut dans le pool "default")
  Supprimer volume qcow2 : fait
  cree une vm (template ??)
"""


# Storage utils


def isVolumeExist(pool, volName):
    if pool.isActive():
        for name in pool.listVolumes():
            if name == volName:
                return True
    return False


def createStoragePoolVolume(pool, volName, capacity):
    if not isVolumeExist(pool, volName):
        stpVolXML = (
            """
            <volume>
              <name>"""
            + volName
            + """</name>
              <allocation>0</allocation>
              <capacity unit="G">"""
            + str(capacity)
            + """</capacity>
              <target>
                <format type="qcow2"/>
              </target>
            </volume>
            """
        )
        stpVol = pool.createXML(stpVolXML, 0)
        return stpVol
    else:
        return "Volume already exist"


def deleteStoragePoolVolume(volume):
    volume.delete()


def list_storage_pool(conn):
    pools = conn.listAllStoragePools(0)

    for pool in pools:
        if pool.isActive():
            stgvols = pool.listVolumes()
            print("Storage pool: " + pool.name())

            for stgvol in stgvols:
                print("     Storage vol: " + stgvol)


# VM utils
def get_domain_xml(conn, uuid):
    domain = conn.lookupByUUIDString(uuid)
    xml_desc = domain.XMLDesc()
    return xml_desc


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

    return hypervisor_info


def destroy_vm(domain):
    if domain.isActive():
        domain.destroy()
    else:
        print("domain is already innactive")


def start_vm(domain):
    if domain.isActive():
        print("VM is already active")
    else:
        domain.create()


# TEST
remote_user = "root"
remote_hosts = "172.16.136.156"

conn = libvirt.open("qemu+ssh://" + remote_user + "@" + remote_hosts + "/system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")


start_vm(conn.lookupByName("eteint"))
destroy_vm(conn.lookupByName("debian11"))
conn.close()
