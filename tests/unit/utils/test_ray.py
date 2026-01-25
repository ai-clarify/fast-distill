# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
from unittest import mock

from fastdistill.utils.ray import script_executed_in_ray_cluster


def test_script_executed_on_ray_cluster() -> None:
    assert not script_executed_in_ray_cluster()

    with mock.patch.dict(
        os.environ,
        {
            "RAY_NODE_TYPE_NAME": "headgroup",
            "RAY_CLUSTER_NAME": "disticluster",
            "RAY_ADDRESS": "127.0.0.1:6379",
        },
    ):
        assert script_executed_in_ray_cluster()
