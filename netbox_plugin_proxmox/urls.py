from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import views, models

urlpatterns = (
    path("import/all", views.ProxmoxStatus.as_view(), name="proxmoxstatus"),
    path("sync/all", views.ProxmoxSync, name="proxmoxsync"),
    # Proxmox Instances / Clusters
    path(
        "proxmox/", views.ProxmoxClusterListView.as_view(), name="proxmoxcluster_list"
    ),
    path(
        "proxmox/add", views.ProxmoxClusterEditView.as_view(), name="proxmoxcluster_add"
    ),
    path(
        "proxmox/<int:pk>/", views.ProxmoxClusterView.as_view(), name="proxmoxcluster"
    ),
    path(
        "proxmox/<int:pk>/edit",
        views.ProxmoxClusterEditView.as_view(),
        name="proxmoxcluster_edit",
    ),
    path(
        "proxmox/<int:pk>/delete",
        views.ProxmoxClusterDeleteView.as_view(),
        name="proxmoxcluster_delete",
    ),
    path(
        "proxmox/<int:pk>/changelog",
        ObjectChangeLogView.as_view(),
        name="proxmoxcluster_changelog",
        kwargs={"model": models.ProxmoxCluster},
    ),
    # Proxmox to NetBox Mapping
    path(
        "netbox-mapping/",
        views.ProxmoxNetboxMappingListView.as_view(),
        name="proxmoxnetboxmapping_list",
    ),
    path(
        "netbox-mapping/add",
        views.ProxmoxNetboxMappingEditView.as_view(),
        name="proxmoxnetboxmapping_add",
    ),
    path(
        "netbox-mapping/<int:pk>/",
        views.ProxmoxNetboxMappingView.as_view(),
        name="proxmoxnetboxmapping",
    ),
    path(
        "netbox-mapping/<int:pk>/edit",
        views.ProxmoxNetboxMappingEditView.as_view(),
        name="proxmoxnetboxmapping_edit",
    ),
    path(
        "netbox-mapping/<int:pk>/delete",
        views.ProxmoxNetboxMappingDeleteView.as_view(),
        name="proxmoxnetboxmapping_delete",
    ),
    path(
        "netbox-mapping/<int:pk>/changelog",
        ObjectChangeLogView.as_view(),
        name="proxmoxnetboxmapping_changelog",
        kwargs={"model": models.ProxmoxNetboxMapping},
    ),
)
