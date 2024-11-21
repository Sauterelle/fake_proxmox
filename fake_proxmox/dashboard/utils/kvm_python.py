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
  cree une vm (template ??)
  ---------Gestion disque---------
  creer un pool 
  Cree un volume qcow2 : fait (par défaut dans le pool "default")
  Supprimer volume qcow2 : fait
"""


# Storage utils


def isVolumeExist(pool, volName):
    if pool.isActive():
        for name in pool.listVolumes():
            if name == volName:
                return True
    return False


def createStoragePoolVolume(pool, volName, capacity=10):
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


def createVm(conn, name, volume, vcpu=1, memory=1):
    xml_config = (
        """
        <domain type='qemu'>
        <name>"""
        + name
        + """</name>
        <memory unit='G'>"""
        + str(memory)
        + """</memory> <!-- 1 Go de RAM -->
        <vcpu placement='static'>"""
        + str(vcpu)
        + """</vcpu>    <!-- 1 vCPU -->
        <os>
            <type arch='x86_64' machine='pc-i440fx-7.2'>hvm</type>
        </os>
        <devices>
            <disk type='file' device='disk'>
            <driver name='qemu' type='qcow2'/>
            <source file='"""
        + volume.path()
        + """'/>
            <target dev='vda' bus='virtio'/>
            </disk>
            <interface type='network'>
            <source network='default'/>
            </interface>
        </devices>
        </domain>
        """
    )

    dom = conn.createXML(xml_config)

    if dom is None:
        print("Failed to create a domain fom an XML definition.")
        exit(1)
    print("Guest " + dom.name() + " has booted")


def destroyVm(domain):
    if domain.isActive():
        domain.destroy()
    else:
        print("domain is already innactive")


def startVm(domain):
    if domain.isActive():
        print("VM is already active")
    else:
        domain.create()
