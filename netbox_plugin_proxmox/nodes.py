import logging
from dcim.models import devices as nb_devices
from .utils import (
    get_or_create_vlan,
    get_or_create_ip,
    get_or_create_interface,
)
from .vms import get_or_create_and_update_qemu, get_or_create_and_update_lxc


logger = logging.getLogger(__name__)


def get_or_create_and_update_node(
    node_proxmox_json, netbox_cluster, proxmox_client, netbox_config
):
    logger.info(f"Working on node {node_proxmox_json.get('name')}")
    yield f"<p>Working on node {node_proxmox_json.get('name')}</p>"
    try:
        nb_node = nb_devices.Device.objects.get(name=node_proxmox_json.get("name"))
        nb_node.status = "active" if node_proxmox_json.get("online") == 1 else "offline"
    except nb_devices.Device.DoesNotExist:
        nb_node = nb_devices.Device(
            name=node_proxmox_json.get("name"),
            device_type_id=netbox_config.get("node_device_type_id"),
            role_id=netbox_config.get("node_role_id"),
            site_id=netbox_config.get("site_id"),
            status="active" if node_proxmox_json.get("online") == 1 else "offline",
        )

    primary_ip4 = get_or_create_ip(node_proxmox_json.get("ip"))
    nb_node.primary_ip4 = primary_ip4
    nb_node.cluster = netbox_cluster
    nb_node.save()
    cluster_mgmt = get_or_create_interface(if_name="cluster_mgmt", device_id=nb_node.id)
    cluster_mgmt.mgmt_only = True
    cluster_mgmt.save()
    primary_ip4.assigned_object = cluster_mgmt
    primary_ip4.save()
    eth = []
    virt = []
    bond = []
    bridge = []
    other = []
    for pmx_interfaces in proxmox_client.nodes(
        node_proxmox_json.get("name")
    ).network.get():
        match pmx_interfaces.get("type"):
            case "eth":
                eth.append(pmx_interfaces)
            case "OVSIntPort":
                virt.append(pmx_interfaces)
            case "OVSBond":
                bond.append(pmx_interfaces)
            case "OVSBridge":
                bridge.append(pmx_interfaces)
            case _:
                other.append(pmx_interfaces)
    for iface in eth:
        yield from get_or_create_and_update_node_interface(
            iface, nb_node, netbox_config
        )
    for iface in virt:
        yield from get_or_create_and_update_node_interface(
            iface, nb_node, netbox_config
        )
    for iface in bond:
        yield from get_or_create_and_update_node_interface(
            iface, nb_node, netbox_config
        )
    for iface in bridge:
        yield from get_or_create_and_update_node_interface(
            iface, nb_node, netbox_config
        )
    for sdn_zone in proxmox_client.nodes(node_proxmox_json.get("name")).sdn.zones.get():
        for sdn_bridge in (
            proxmox_client.nodes(node_proxmox_json.get("name"))
            .sdn.zones(sdn_zone.get("zone"))
            .content.get()
        ):
            yield from get_or_create_and_update_node_interface(
                {
                    "iface": sdn_bridge.get("vnet"),
                    "ovs_type": "OVSBridge",
                    "mtu": "9000",
                    "type": "OVSBridge",
                },
                nb_node,
                netbox_config,
            )

    for qemu in sorted(
        proxmox_client.nodes(node_proxmox_json.get("name")).qemu.get(),
        key=lambda d: d["vmid"],
    ):
        yield from get_or_create_and_update_qemu(
            qemu,
            netbox_config,
            netbox_cluster,
            nb_node,
            node_proxmox_json.get("name"),
            proxmox_client,
        )

    for lxc in proxmox_client.nodes(node_proxmox_json.get("name")).lxc.get():
        yield from get_or_create_and_update_lxc(lxc, netbox_config)


def get_or_create_and_update_node_interface(
    proxmox_interface, netbox_node, netbox_config
):
    logger.info(f"Working on interface {proxmox_interface.get('iface')}")
    yield f"<p>Working on interface {proxmox_interface.get('iface')}</p>"
    if proxmox_interface.get("ovs_tag") is not None:
        tagged_vlans = int(proxmox_interface.get("ovs_tag"))
    else:
        tagged_vlans = None

    nb_iface = get_or_create_interface(proxmox_interface.get("iface"), netbox_node.id)
    if tagged_vlans:
        nb_iface.mode = "tagged"
        nb_iface.tagged_vlans.set([get_or_create_vlan(tagged_vlans)])
        nb_iface.save()

    iface_type = None
    match proxmox_interface.get("type"):
        case "eth":
            if not netbox_config.get("keep_interface_config"):
                iface_type = "other"
        case "OVSIntPort":
            iface_type = "virtual"
        case "OVSBond":
            iface_type = "lag"
            for bond_member in proxmox_interface.get("ovs_bonds", "").split(" "):
                nb_bond_member = get_or_create_interface(bond_member, netbox_node.id)
                nb_bond_member.lag = nb_iface
                nb_bond_member.save()
        case "OVSBridge":
            iface_type = "bridge"
            for bridge_member in proxmox_interface.get("ovs_ports", "").split(" "):
                nb_bridge_member = get_or_create_interface(
                    bridge_member, netbox_node.id
                )
                nb_bridge_member.bridge = nb_iface
                nb_bridge_member.save()
        case _:
            if not netbox_config.get("keep_interface_config"):
                iface_type = "other"
    if iface_type is not None:
        nb_iface.type = iface_type
        nb_iface.save()

    if proxmox_interface.get("cidr"):
        nb_ip = get_or_create_ip(proxmox_interface.get("cidr"))
        nb_ip.assigned_object_id = nb_iface.id
        nb_ip.assigned_object = nb_iface
        nb_ip.description = netbox_node.name
        nb_ip.save()

    nb_iface.mtu = int(proxmox_interface.get("mtu") or 1500)
    nb_iface.save()
