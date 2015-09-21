"""
Copyright 2015 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest

from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.config import ComputeConfig
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.common.tools.datagen import rand_name

from cloudroast.compute.instance_actions.api.test_resize_server_down \
    import ResizeServerDownConfirmTests, ResizeDownConfirmBaseFixture
from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture


# This is for setting the resize type and hypervisor based on configs
compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()

flavors_config = FlavorsConfig()
resize_down_enabled = (flavors_config.resize_down_enabled
                     if flavors_config.resize_down_enabled is not None
                     else flavors_config.resize_enabled)

can_resize = (
    resize_down_enabled
    and hypervisor not in [ComputeHypervisors.IRONIC,
                           ComputeHypervisors.LXC_LIBVIRT])


@unittest.skipUnless(
    can_resize, 'Resize not enabled due to the flavor class or hypervisor.')
class ServerFromVolumeV1ResizeDownConfirmTests(ServerFromVolumeV1Fixture,
                                               ResizeServerDownConfirmTests,
                                               ResizeDownConfirmBaseFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates a keypair.
            - Creates an active server.
            - Resizes the server down.
        """
        super(ServerFromVolumeV1ResizeDownConfirmTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(flavor_ref=cls.flavor_ref_alt, key_name=cls.key.name)
        cls.resize_down_and_confirm()

    @unittest.skip("Skipped as BFV server disk size does not change on resize.")
    def test_created_server_disk_size(self):
        pass
