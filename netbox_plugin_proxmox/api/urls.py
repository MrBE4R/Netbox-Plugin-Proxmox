from netbox.api.routers import NetBoxRouter
from . import views


app_name = "netbox_plugin_proxmox"

router = NetBoxRouter()
router.register("proxmox-cluster", views.ProxmoxClusterViewSet)
router.register("netbox-mapping", views.ProxmoxNetboxMappingViewSet)

urlpatterns = router.urls
