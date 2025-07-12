from netbox.forms import NetBoxModelForm
from .models import ProxmoxCluster, ProxmoxNetboxMapping


class ProxmoxClusterForm(NetBoxModelForm):
    class Meta:
        model = ProxmoxCluster
        fields = (
            "proxmox_url",
            "verify_tls",
            "username",
            "token_name",
            "token_value",
            "enabled",
            "netbox_mapping",
        )


class ProxmoxNetboxMappingForm(NetBoxModelForm):
    class Meta:
        model = ProxmoxNetboxMapping
        fields = (
            "name",
            "site",
            "cluster_type",
            "node_role",
            "node_device_type",
            "vm_role",
        )
