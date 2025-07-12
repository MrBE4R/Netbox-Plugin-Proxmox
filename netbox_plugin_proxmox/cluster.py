import logging
from dcim.models import devices as nb_devices
from proxmoxer import ProxmoxAPI
from virtualization.models import clusters as nb_clusters
from .models import ProxmoxCluster
from .nodes import get_or_create_and_update_node


logger = logging.getLogger(__name__)


def get_or_create_and_update_clusters(cluster_id: int = None):
    if cluster_id:
        logger.info(f"We should run import only for cluster with id : {cluster_id}")
        yield f"<p>We should run import only for cluster with id : {cluster_id}</p>"
    else:
        config = {
            "clusters": [
                x.to_config_dict() for x in ProxmoxCluster.objects.filter(enabled=True)
            ],
        }
        logger.info(f"Got {len(config.get('clusters'))} Proxmox Cluster or Instances")
        yield f"<p>Got {len(config.get('clusters'))} Proxmox Cluster or Instances</p>"
        for cluster in config.get("clusters"):
            logger.info(f"Working on Proxmox located at {cluster.get('url')}")
            yield f"<p>Working on Proxmox located at {cluster.get('url')}</p>"
            pmx = ProxmoxAPI(
                host=cluster.get("url"),
                user=cluster.get("username"),
                token_name=cluster.get("token").get("name"),
                token_value=cluster.get("token").get("value"),
                verify_ssl=cluster.get("verify_ssl"),
            )
            pmx_cluster = [
                x for x in pmx.cluster.status.get() if x.get("type") == "cluster"
            ]
            pmx_cluster = pmx_cluster[0] if pmx_cluster else None
            if pmx_cluster is not None:
                nb_cfg = cluster.get("netbox")
                try:
                    nb_cluster = nb_clusters.Cluster.objects.get(
                        name=pmx_cluster.get("name")
                    )
                except nb_clusters.Cluster.DoesNotExist:
                    nb_cluster = nb_clusters.Cluster(
                        name=pmx_cluster.get("name"),
                        type_id=nb_cfg.get("cluster_type_id"),
                        status="active",
                    )
                    nb_cluster.save()
                proxmox_nodes = [
                    x
                    for x in sorted(pmx.cluster.status.get(), key=lambda d: d["name"])
                    if x.get("type") == "node"
                ]
                logger.info(f"Cluster has {len(proxmox_nodes)} nodes")
                yield f"<p>Cluster has {len(proxmox_nodes)} nodes</p>"
                for node in proxmox_nodes:
                    yield from get_or_create_and_update_node(
                        node_proxmox_json=node,
                        netbox_cluster=nb_cluster,
                        proxmox_client=pmx,
                        netbox_config=nb_cfg,
                    )
                logger.info("Cleaning old cluster nodes")
                yield "<p>Cleaning old cluster nodes</p>"
                proxmox_nodes_names = [x.get("name") for x in proxmox_nodes]
                netbox_nodes_names = [
                    x.name for x in nb_cluster.devices.order_by("name").all()
                ]
                for nb_node in netbox_nodes_names:
                    if nb_node not in proxmox_nodes_names:
                        logger.info(
                            f"Node {nb_node} is no longer member of the cluster, removing."
                        )
                        yield f"<p>Node {nb_node} is no longer member of the cluster, removing.</p>"
                        node = nb_devices.objects.get(name=nb_node, cluster=nb_cluster)
                        node.delete()
            else:
                logger.error("Could not get proxmox status")
