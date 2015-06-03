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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import NovaServerStatusTypes, \
    InstanceAuthStrategies
from cloudroast.compute.fixtures import ServerFromImageFixture
from cloudcafe.compute.composites import ComputeAdminComposite


class EvacuateServerTest(object):

    @tags(type='smoke', net='no')
    def test_evacuate_server_on_same_cell(self):
        """
        Verify that a server can be evacuated successfully.

        Get the server that was created in setup and use it to call evacuate
        server and waits for status active, once it confirms
        the status, it will check to see if the actual host was changed

        This test will be successful if:
            - The server went to Active status
            - The host was changed
        """
        self.new_password = "newslice129690TuG72Bgj2"

        # Evacuate and wait for ACTIVE status
        self.compute_admin.servers.client.evacuate(self.server.id,
                                                   host=self.host_before_evacuate,
                                                   on_shared_storage=False,
                                                   admin_pass=self.new_password)
        server_after_evacuate = self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE).entity

        # Check that compute node is changed
        self.assertNotEqual(
            self.compute_host_name.host, server_after_evacuate.host,
            msg="Host is not changed after evacuation, source host is {host_before} "
                "destination host is {host_after}".format(
                    host_before=self.compute_host_name.host,
                    host_after=server_after_evacuate.host))

        # Get server details
        server = self.servers_client.get_server(self.server.id).entity

        # Set the server's admin_pass attribute to the new password
        server.admin_pass = self.new_password

        public_address = self.server_behaviors.get_public_ip_address(server)
        # Get an instance of the remote client
        remote_client = self.server_behaviors.get_remote_instance_client(
            server, config=self.servers_config,
            auth_strategy=InstanceAuthStrategies.PASSWORD)

        self.assertTrue(
            remote_client.can_authenticate(),
            "Could not connect to server {uuid} with ip {ip} using new "
            " admin password {new_password} "
            (uuid=server.id, ip=public_address, new_password=self.new_password))


class ServerFromImageEvacuateTests(ServerFromImageFixture,
                                   EvacuateServerTest):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are accessed from a parent class:
            - An instance from ServerFromImageEvacuateTests.

        The following resources are created during this setup:
            - Initializes compute admin.
            - Create a server from server behaviors.
        """
        super(ServerFromImageEvacuateTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.create_server()

        cls.compute_host_name = cls.compute_admin.servers.client.get_server(
            cls.server.id).entity
        host_list = cls.compute_admin.hosts.client.list_hosts()
        for host in host_list.entity:
            if cls.compute_host_name.host in host.host_name:
                cls.host_before_evacuate = host.host_name
        host_response = cls.compute_admin.hosts.client.\
            update_host(cls.compute_host_name.host, status="disable").entity

    @classmethod
    def tearDownClass(cls):
        super(ServerFromImageEvacuateTests, cls).tearDownClass()
        cls.compute_admin.hosts.client.\
            update_host(cls.compute_host_name.host, status="enable").entity
