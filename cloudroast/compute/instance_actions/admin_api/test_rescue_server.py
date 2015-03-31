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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.config import ComputeConfig

from cloudroast.compute.fixtures import ComputeAdminFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.IRONIC, ComputeHypervisors.LXC_LIBVIRT],
    'Rescue server not supported in current configuration.')
class ServerAdminRescueTests(object):

    @tags(type='smoke', net='yes')
    def test_rescue_and_unrescue_server_as_admin_test(self):
        """
        Verify that a server can be rescued via Admin successfully.

        Get the server that was created in setup and use it to call rescue
        server and waits for status rescue, once it confirms
        the rescue, it will un-rescue and after that will verify the server
        reached active status

        The following assertions occur:
            - The response status code to the rescue request is equal to 200
            - The admin password of the server in RESCUE status is not equal to
            the admin password of the server prior to rescue
            - The response status code to the unrescue request is equal to 200
        """

        rescue_response = self.admin_rescue_client.rescue(self.server.id)
        changed_password = rescue_response.entity.admin_pass
        self.assertEqual(rescue_response.status_code, 200)
        self.assertTrue(self.server.admin_pass is not changed_password,
                        msg="The password did not change after Rescue.")

        # Enter rescue mode
        self.server_behaviors.wait_for_server_status(
            self.server.id, 'RESCUE')

        # Exit rescue mode
        unrescue_response = self.admin_rescue_client.unrescue(self.server.id)
        self.assertEqual(unrescue_response.status_code, 202)
        self.server_behaviors.wait_for_server_status(self.server.id, 'ACTIVE')


class RescueServerAsAdminTests(ComputeAdminFixture,
                               ServerAdminRescueTests):
    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Create Keypair
            - Create a server from server behaviors.
        """
        super(RescueServerAsAdminTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            key_name=cls.key.name).entity
        flavor_response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = flavor_response.entity
