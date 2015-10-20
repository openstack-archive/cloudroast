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
    hypervisor in [ComputeHypervisors.LXC_LIBVIRT],
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
        get a remote client for the server and validate that the number of
        disks on the server after being rescued and unrescued is equal to the
        number of disks originally on the server.

        The following assertions occur:
            - The response status code of a rescue request is equal to 200
            - The server password is different after the server rescue request
            - If the image os_type metadata type is not windows, the number of
              disks on the rescued server should be equal to one plus the
              number of disks originally on the server
            - The response status code of an unrescue request is equal to 202
            - When the server has exited RESCUE statue the number of disks on
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
                password=changed_password, auth_strategy='password')
            disks = remote_client.get_all_disks()

            # Xen VMs create another VM with a clean image of original
            # server and the image of the VM needing rescue where as Ironic
            # defaults to the underlying OS.
            if hypervisor != ComputeHypervisors.IRONIC:
                self.assertEqual(len(disks.keys()), original_num_disks + 1)
            else:
                self.assertEqual(len(disks.keys()), original_num_disks)

        # Exit rescue mode
        unrescue_response = self.rescue_client.unrescue(self.server.id)
        self.assertEqual(unrescue_response.status_code, 202)
        self.server_behaviors.wait_for_server_status(self.server.id, 'ACTIVE')
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config,
            key=self.key.private_key)
        disks = remote_client.get_all_disks()
        self.assertEqual(len(disks.keys()), original_num_disks)

    @unittest.skipIf(
        hypervisor in [ComputeHypervisors.IRONIC],
        'Rescue with image change is not supported in current configuration')
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
        # We cannot access rescued Windows servers, so skip
        # this portion of the validation in that case.
        image = self.images_client.get_image(self.server.image.id).entity
        if image.metadata.get('os_type', '').lower() != 'windows':
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

        # We cannot access rescued Windows servers, so skip
        # this portion of the validation in that case.
        image_resp = self.images_client.get_image(self.server.image.id)
        self.assertEqual(image_resp.status_code, 200)
        image = image_resp.entity
        if image.metadata.get('os_type', '').lower() != 'windows':

            # Test distro change after rescue with image supplied
            remote_client = self.server_behaviors.get_remote_instance_client(
                server, self.servers_config, password=changed_password,
                key=self.key.private_key)
            distro_after_rescue = remote_client.get_distribution_and_version()

            if (distro_before_rescue and distro_after_rescue):
                if self.image_ref != self.image_ref_alt:
                    self.assertNotEqual(
                        distro_before_rescue, distro_after_rescue)
                else:
                    self.assertEqual(distro_before_rescue, distro_after_rescue)
            else:
                raise Exception('Unable to retrieve distros for rebuild check')

        # Exit rescue mode
        unrescue_response = self.rescue_client.unrescue(server.id)
        self.assertEqual(unrescue_response.status_code, 202)
        self.server_behaviors.wait_for_server_status(server.id,
                                                     'ACTIVE')

    @tags(type='smoke', net='yes')
    def test_rescue_and_delete_server_test(self):
        """
        Verify that a server can enter a rescue mode and then be deleted.

        Rescue the server and validate that the response status code is 200
        and that the password to access the server has changed. Wait for
        the server to achieve 'RESCUE' status. Delete the
        server and verify that a rescued server can be deleted.

        The following assertions occur:
            - The response status code of a rescue request is equal to 200
            - The response status code of a delete request for rescued server
              is equal to 204
            - The rescued server is deleted.
        """

        rescue_response = self.rescue_client.rescue(self.server.id)
        self.assertEqual(rescue_response.status_code, 200,
                         msg="Rescuing server {0} failed with response code"
                         " {1}".format(self.server.id, rescue_response.status_code))
        changed_password = rescue_response.entity.admin_pass
        self.assertTrue(self.server.admin_pass is not changed_password,
                        msg="The password did not change after Rescue.")

        # Enter rescue mode
        self.server_behaviors.wait_for_server_status(self.server.id, 'RESCUE')

        # Delete the server when in rescue mode
        delete_response = self.servers_client.delete_server(self.server.id)
        self.assertEqual(204, delete_response.status_code,
                         msg="Deleting server {0} failed with response code"
                         " {1}".format(self.server.id, rescue_response.status_code))

        # confirm deletion
        self.server_behaviors.wait_for_server_to_be_deleted(self.server.id)


class ServerFromImageRescueTests(ServerFromImageFixture,
                                 ServerRescueTests):

    def setUp(self):
        """
        Perform actions that set up the necessary resources for testing

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - The keypair previously created
                - Remaining values required for creating a server will come
                  from test configuration.
        """
        super(ServerFromImageRescueTests, self).setUp()
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name,
                           self.keypairs_client.delete_keypair)
        self.create_server(key_name=self.key.name)
        flavor_response = self.flavors_client.get_flavor_details(self.flavor_ref)
        self.flavor = flavor_response.entity
