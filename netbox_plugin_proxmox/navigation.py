from django.utils.translation import gettext_lazy as _
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem
from netbox.plugins.utils import get_plugin_config

menu_name = get_plugin_config("netbox_plugin_proxmox", "menu_name")
top_level_menu = get_plugin_config("netbox_plugin_proxmox", "top_level_menu")

_menu_items = (
    PluginMenuItem(
        link="plugins:netbox_plugin_proxmox:proxmoxstatus",
        link_text="Run Import",
    ),
    PluginMenuItem(
        link="plugins:netbox_plugin_proxmox:proxmoxcluster_list",
        link_text="Proxmox Cluster or Instance",
    ),
    PluginMenuItem(
        link="plugins:netbox_plugin_proxmox:proxmoxnetboxmapping_list",
        link_text="Proxmox to Netbox Mapping",
    ),
)

if top_level_menu:
    menu = PluginMenu(
        label=menu_name,
        groups=(
            (
                _("Import and Config"),
                _menu_items,
            ),
        ),
        icon_class="mdi mdi-application-import",
    )
else:
    menu_items = _menu_items
