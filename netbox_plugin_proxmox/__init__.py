from netbox.plugins import PluginConfig


class NetBoxProxmoxConfig(PluginConfig):
    name = "netbox_plugin_proxmox"
    verbose_name = " NetBox Plugin Proxmox"
    description = "Plugins to automatically sync virtual machines from multiples proxmox cluster or instances"
    version = "2025.07.14"
    min_version = "4.3.0"
    base_url = "netbox-proxmox"
    author = "Jean-François GUILLAUME"
    author_email = "jean-francois.guillaume@univ-nantes.fr"
    required_settings = []
    defaults_settings = {"top_level_menu": True, "menu_name": "Netbox Proxmox Importer"}


config = NetBoxProxmoxConfig
