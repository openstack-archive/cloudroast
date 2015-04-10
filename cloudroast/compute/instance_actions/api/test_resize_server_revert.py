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
from cloudcafe.compute.common.types import ComputeHypervisors, \
    NovaServerStatusTypes
from cloudcafe.compute.config import ComputeConfig
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()

flavors_config = FlavorsConfig()
resize_enabled = flavors_config.resize_enabled

can_resize = (
    resize_enabled
    and hypervisor not in [ComputeHypervisors.IRONIC,
                           ComputeHypervisors.LXC_LIBVIRT])


class ResizeServerUpRevertTests(object):

    @tags(type='smoke', net='no')
    def test_server_properties_after_resize(self):
        self.assertEqual(self.flavor_ref, self.server.flavor.id)

    @tags(type='smoke', net='yes')
    def test_resize_reverted_server_vcpus(self):
        """
        vCPUs of resized reverted server is equal to the original flavor's vCPUs

        Get a remote client for the server resized and reverted during test set
        up. Use the remote client to get the number of CPUs for the server.
        Validate that this value is equal to the vCPUs of the flavor from test
        configuration.

        The following validations occur:
            - The vCPUs value of the flavor from test configuration is equal
              to the number of CPUs on the server resized and reverted during
              test set up
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, key=self.key.private_key)
        server_actual_vcpus = remote_client.get_number_of_cpus()
        self.assertEqual(
            server_actual_vcpus, self.flavor.vcpus,
            msg="Expected number of vcpus to be {0}, was {1}.".format(
                self.flavor.vcpus, server_actual_vcpus))

    @tags(type='smoke', net='yes')
    def test_resize_reverted_server_disk_size(self):
        """
        Disks of resized reverted server is equal to the original flavor's disks

        The virtual disk size of a resize reverted server should be equal to the
        disk size of the flavor used to originally create the server. Get a
        remote client for the server resized and reverted during test setup. Use
        the remote client to get the disk size of the server. Validate that the
        disk size of the server is equal to the disk size of the flavor from
        test configuration.

        The following assertions occur:
            - The disk size of the server resized and reverted during test set
              up is equal to the disk size of the flavor from test
              configuration.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.flavor.disk, disk_size))

    @tags(type='smoke', net='yes')
    def test_can_log_into_resize_reverted_server(self):
        """
        Resized reverted server is accessible using a remote instance client

        Get a remote instance client for the server resized and reverted during
        test set up. Validate that the remote instance client can authenticate
        to the server.

        The following assertions occur:
            - The remote client for the server resized and reverted during test
              set up can authenticate to the server
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, key=self.key.private_key)
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot connect to server using public ip")

    @tags(type='smoke', net='yes')
    def test_ram_after_resize_revert(self):
        """
        RAM of a reverted resized server should be set to the original flavor

        Get a remote instance client for the instance resized and reverted
        during test set up. Calculate the minimum acceptable RAM value, this is
        90% of the RAM value of the flavor from test configuration. Validate
        that the RAM of the server is equal to the RAM value of the flavor from
        the test configuration or greater than/equal to the minimum RAM value
        previously calculated.

        The following assertions occur:
            - The RAM value of the server resized during test set up is equal
              to the RAM value of the flavor from test configuration or
              greater than/equal to a value that is 90% of the RAM value of the
              flavor from test configuration
        """

        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        lower_limit = int(self.flavor.ram) - (int(self.flavor.ram) * .1)
        server_ram_size = int(remote_instance.get_allocated_ram())
        self.assertTrue((int(self.flavor.ram) == server_ram_size
                         or lower_limit <= server_ram_size),
                        msg='Ram size after revert-resize did not match.'
                            'Expected ram size : %s, Actual ram size : %s' %
                            (self.flavor.ram, server_ram_size))

    @tags(type='smoke', net='no')
    def test_resize_reverted_server_instance_actions(self):
        """
        Verify the correct actions are logged during a server resize revert.

        Get the list of all actions that the server has taken from the Nova API.
        Filter the list so that only the actions 'resize' remain. Validate that
        the list of filtered actions has a length of 1 (that only 1 resize
        action has been performed.) Validate that the values of the identified
        create action match the values returned in the create server response
        received during test setup. Filter the list so that only the actions
        'revertResize' remain. Validate that the list of filtered actions has a
        length of 1 (that only 1 revertResize action has been performed.)
        Validate that the values of the identified create action match the
        values returned in the create server response received during test
        setup.

        The following assertions occur:
            - The list of actions that match 'resize' has only one item
            - The values for the resize action match the values received in
              response to the create request
            - The list of actions that match 'revertResize' has only one item
            - The values for the revertResize action match the values received
              in response to the resize request
        """
        actions = self.servers_client.get_instance_actions(
            self.server.id).entity

        # Verify the resize action is listed
        self.assertTrue(any(a.action == 'resize' for a in actions))
        filtered_actions = [a for a in actions if a.action == 'resize']
        self.assertEquals(len(filtered_actions), 1)

        resize_action = filtered_actions[0]
        self.validate_instance_action(
            resize_action, self.server.id, self.compute.user.user_id,
            self.compute.user.project_id,
            self.resize_resp.headers['x-compute-request-id'])

        # Verify the revert resize action is listed
        self.assertTrue(any(a.action == 'revertResize' for a in actions))
        filtered_actions = [a for a in actions if a.action == 'revertResize']
        self.assertEquals(len(filtered_actions), 1)

        resize_action = filtered_actions[0]
        self.validate_instance_action(
            resize_action, self.server.id, self.compute.user.user_id,
            self.compute.user.project_id,
            self.revert_resize_resp.headers['x-compute-request-id'])


class ResizeUpRevertBaseFixture(object):

    @classmethod
    def resize_up_and_revert(self):
        """
        Resize a server, revert the resize and wait for it to become active

        Resize the server created during test setup using the flavor from
        test configurations. Wait for the server to enter 'VERIFY_RESIZE' state.
        Revert the resize and wait for the server to enter 'ACTIVE' state.
        """
        server_to_resize = self.server
        # resize server and revert
        self.resize_resp = self.servers_client.resize(
            server_to_resize.id, self.flavor_ref_alt)
        self.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.VERIFY_RESIZE)

        self.revert_resize_resp = self.servers_client.revert_resize(
            server_to_resize.id)
        self.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.ACTIVE)
        resized_server_response = self.servers_client.get_server(
            server_to_resize.id)

        self.server = resized_server_response.entity
        self.server.admin_pass = server_to_resize.admin_pass
        self.resized_flavor = self.flavors_client.get_flavor_details(
            self.flavor_ref_alt).entity


@unittest.skipUnless(
    can_resize, 'Resize not enabled due to the flavor class or hypervisor.')
class ServerFromImageResizeServerUpRevertTests(ServerFromImageFixture,
                                               ResizeServerUpRevertTests,
                                               ResizeUpRevertBaseFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that set up the necessary resources for testing

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - The keypair previously created
                - Remaining values required for creating a server will come
                  from test configuration.

        The following actions are performed during this set up:
            - The server is resized and then reverted
        """
        super(ServerFromImageResizeServerUpRevertTests, cls).setUpClass()
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
        cls.resize_up_and_revert()
