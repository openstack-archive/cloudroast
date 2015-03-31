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

from cloudroast.compute.decorators import requires_extension
from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.IRONIC, ComputeHypervisors.LXC_LIBVIRT],
    'Rescue server not supported in current configuration.')
class ServerRescueTests(object):

    @tags(type='smoke', net='yes')
    def test_rescue_and_unrescue_server_test(self):
        """
        Verify that a server can enter and exit rescue mode

        Get a remote client for the server created during test set up. Use the
        remote client to get a list of all disks on the server. Rescue the
        server and validate that the response status code is 202 and that the
        password to access the server has changed. Wait for the server to
        achieve 'RESCUE' status. If the server is not a Windows server, get a
        remote client for the rescued server and validate that the number of
        disks on the server is equal to one plus the number of disks originally
        on the server. Unrescue the server and once it reaches 'ACTIVE' status
        get a remote client for the server and validate that the number of disks
        on the server after being rescued and unrescued is equal to the number
        of disks originally on the server.

        The following assertions occur:
            - The response status code of a rescue request is equal to 200
            - The server password is different after the server rescue request
            - If the image os_type metadata type is not windows, the number of
              disks on the rescued server should be equal to one plus the number
              of disks originally on the server
            - The response status code of an unrescue request is equal to 202
            - When the server has exited RESCUE statue ths number of disks on
              the server should be equal to the number of disks originally on
              the server

        """

        # Get the number of disks the server has
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config,
            key=self.key.private_key)
        disks = remote_client.get_all_disks()
        original_num_disks = len(disks.keys())

        rescue_response = self.rescue_client.rescue(self.server.id)
        changed_password = rescue_response.entity.admin_pass
        self.assertEqual(rescue_response.status_code, 200)
        self.assertTrue(self.server.admin_pass is not changed_password,
                        msg="The password did not change after Rescue.")

        # Enter rescue mode
        rescue_server_response = self.server_behaviors.wait_for_server_status(
            self.server.id, 'RESCUE')
        rescue_server = rescue_server_response.entity
        rescue_server.admin_pass = changed_password

        # We cannot access rescued Windows servers, so skip
        # this portion of the validation in that case.
        image = self.images_client.get_image(self.server.image.id).entity
        if image.metadata.get('os_type', '').lower() != 'windows':

            # Verify if original disks plus rescue disk are attached
            remote_client = self.server_behaviors.get_remote_instance_client(
                rescue_server, self.servers_config,
                key=self.key.private_key)
            disks = remote_client.get_all_disks()
            self.assertEqual(len(disks.keys()), original_num_disks + 1)

        # Exit rescue mode
        unrescue_response = self.rescue_client.unrescue(self.server.id)
        self.assertEqual(unrescue_response.status_code, 202)
        self.server_behaviors.wait_for_server_status(self.server.id, 'ACTIVE')
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config,
            key=self.key.private_key)
        disks = remote_client.get_all_disks()
        self.assertEqual(len(disks.keys()), original_num_disks)

    @requires_extension('ExtendedRescueWithImage')
    @tags(type='smoke', net='yes')
    def test_rescue_with_image_change_server_test(self):
        """
        A server can be rescued using a specified image id

        Verify that a server can enter and exit rescue mode when an image is
        supplied to the rescue request. This test will execute only if the
        extension is enabled. This is determined automatically. Create a server
        using the key created during test set up. Get the distro of the created
        server. Rescue the server using the alt image ref value from test
        configuration as the rescue image ref value. Wait for the server to
        reach 'RESCUE' status. Get a remote instance client for the server and
        use it to get the distro of the rescued server. Validate that if the
        distro should be different, it is different.

        The following assertions occur:
            - The response status code of a rescue request is equal to 200
            - If the image id and the alt image id in test configuration are
              different, the distro of the server before rescue and the distro
              after rescue should be different.
            - If the image id and the alt image id in test configuration are
              the same, the distro of the server before rescue and the distro
              after rescue should be the same.
            - The response status code of an unrescue request is equal to 202
        """
        server = self.create_server(key_name=self.key.name)
        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config, key=self.key.private_key)
        distro_before_rescue = remote_client.get_distribution_and_version()

        # Rescue server with image supplied to rescue request
        rescue_response = self.rescue_client.rescue(
            server.id,
            rescue_image_ref=self.image_ref_alt)
        self.assertEqual(rescue_response.status_code, 200)
        changed_password = rescue_response.entity.admin_pass

        # Enter rescue mode
        rescue_server_response = self.server_behaviors.wait_for_server_status(
            server.id, 'RESCUE')
        rescue_server = rescue_server_response.entity
        rescue_server.admin_pass = changed_password

        # Test distro change after rescue with image supplied
        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config, password=changed_password,
            key=self.key.private_key)
        distro_after_rescue = remote_client.get_distribution_and_version()

        if (distro_before_rescue and distro_after_rescue):
            if self.image_ref != self.image_ref_alt:
                self.assertNotEqual(distro_before_rescue, distro_after_rescue)
            else:
                self.assertEqual(distro_before_rescue, distro_after_rescue)
        else:
            raise Exception('Unable to retrieve distros for rebuild check')

        # Exit rescue mode
        unrescue_response = self.rescue_client.unrescue(server.id)
        self.assertEqual(unrescue_response.status_code, 202)
        self.server_behaviors.wait_for_server_status(server.id,
                                                     'ACTIVE')


class ServerFromImageRescueTests(ServerFromImageFixture,
                                 ServerRescueTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that set up the necessary resources for testing

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with  with the following settings:
                - The keypair previously created
                - Remaining values required for creating a server will come
                  from test configuration.
        """
        super(ServerFromImageRescueTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
        flavor_response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = flavor_response.entity
