# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os


def script_executed_in_ray_cluster() -> bool:
    """Checks if running in a Ray cluster. The checking is based on the presence of
    typical Ray environment variables that are set in each node of the cluster.

    Returns:
        `True` if running on a Ray cluster, `False` otherwise.
    """
    return all(
        env in os.environ
        for env in ["RAY_NODE_TYPE_NAME", "RAY_CLUSTER_NAME", "RAY_ADDRESS"]
    )
