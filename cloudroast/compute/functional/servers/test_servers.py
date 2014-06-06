"""
Copyright 2013 Rackspace

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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.common.types import InstanceAuthStrategies
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeFixture


class ServersTest(ComputeFixture):

    compute_config = ComputeConfig()
    hypervisor = compute_config.hypervisor.lower()

    @unittest.skipIf(
        hypervisor in [ComputeHypervisors.KVM, ComputeHypervisors.QEMU],
        'Password authentication disabled.')
    @tags(type='positive', net='yes')
    def test_create_server_with_admin_password(self):
        """
        If an admin password is provided on server creation, the server's root
        password should be set to that password.
        """
        admin_password = 'oldslice129690TuG72Bgj2'
        response = self.server_behaviors.create_active_server(
            admin_pass=admin_password)
        server = response.entity
        self.resources.add(server.id,
                           self.servers_client.delete_server)

        self.assertEqual(admin_password, server.admin_pass)
        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config, password=admin_password,
            auth_strategy=InstanceAuthStrategies.PASSWORD)
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot authenticate to the server.")

    @tags(type='positive', net='no')
    def test_update_server(self):
        """Update the name and access addresses of a server."""

        response = self.server_behaviors.create_active_server()
        original_server = response.entity
        self.resources.add(
            original_server.id, self.servers_client.delete_server)

        # Use server bookmark's link to update the server
        new_name = rand_name("testserver")
        accessIPv4 = '192.168.32.16'
        accessIPv6 = '3ffe:1900:4545:3:200:f8ff:fe21:67cf'
        updated_server_response = self.servers_client.update_server(
            original_server.id, new_name, accessIPv4=accessIPv4,
            accessIPv6=accessIPv6)
        updated_server = updated_server_response.entity
        self.server_behaviors.wait_for_server_status(
            updated_server.id, NovaServerStatusTypes.ACTIVE)

        # Verify the name and access ips of the server have changed
        server = self.servers_client.get_server(updated_server.id).entity
        self.assertEqual(new_name, server.name,
                         msg="The server name was not updated")
        self.assertEqual(accessIPv4, server.accessIPv4,
                         msg="AccessIPv4 address was not updated")
        self.assertEqual(accessIPv6, server.accessIPv6,
                         msg="AccessIPv6 address was not updated")
        self.assertEqual(server.created, updated_server.created,
                         msg="The server creation date was updated")
        self.assertNotEqual(
            server.updated, original_server.updated,
            msg="Updated time for server {server_id} "
            "did not change after a modification to the server.".format(
                server_id=server.id))
