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
from cloudcafe.compute.common.types import InstanceAuthStrategies
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeFixture

class ServersTest(ComputeFixture):

    compute_config = ComputeConfig()
    hypervisor = compute_config.hypervisor.lower()

    DEFAULT_PSWD_LENGTH = 24

    @unittest.skipIf(
        hypervisor in [ComputeHypervisors.KVM, ComputeHypervisors.QEMU],
        'Password authentication disabled.')
    @tags(type='positive', net='yes')
    def test_create_server_with_admin_password(self):
        """
        Creates a server with an admin password to be used as root's password.

        This will set the server that is created with the root password of
        oldslice129690TuG72Bgj2.  Calls cloudcafe's server behaviors get
        remote instance client with the password to validate that it can
        authenticate wth password.

        The following assertions occur:
            - Defined password is the same as the admin password.
            - get_remote_instance_client has a true value for can_authenticate
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

    @tags(type='positive', net='yes')
    def test_create_server_with_default_password(self):
        """
        Creates a server with a default password set by the provisioning 
        algorithm.

        This will set the server that is created with a default password 
        with a length of 24 characters. Calls cloudcafe's server behaviors get
        remote instance client with the password to validate that it can
        authenticate wth password.

        The following assertions occur:
            - Default password is the correct length.
            - get_remote_instance_client has a true value for can_authenticate

        Design Change: https://jira.rax.io/browse/VIRT-3004
        
        """
        border = '*' * 65

        self.fixture_log.info("\n\n{BORDER}\nCreate a server with a default "
                              "password\n{BORDER}\n\n".format(BORDER=border))
        response = self.server_behaviors.create_active_server()
        server = response.entity
        self.resources.add(server.id, self.servers_client.delete_server)

        # Record expectations and results
        self.fixture_log.info(
            "\n\n{BORDER}\n"
            "Validate Password Length:\n"
            "\tEXPECTED PSWD LENGTH: {EXP}\n"
            "\tACTUAL PSWD LENGTH: {ACT}\n"
            "{BORDER}\n\n".format(
                EXP=self.DEFAULT_PSWD_LENGTH, ACT=len(server.admin_pass),
                BORDER=border))
        self.assertEqual(
            len(server.admin_pass), self.DEFAULT_PSWD_LENGTH,
            "Actual length ({ACTUAL}) does not match the expected length "
            "({EXPECTED})".format(
                EXPECTED=self.DEFAULT_PSWD_LENGTH,
                ACTUAL=len(server.admin_pass)))

        self.fixture_log.info(
            "\n\n{BORDER}\nVerify admin password can be used to log "
            "in.\n{BORDER}\n\n".format(BORDER=border))
        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config, password=server.admin_pass,
            auth_strategy=InstanceAuthStrategies.PASSWORD)
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot authenticate to the server.")

        self.fixture_log.info(
            "\n\n{BORDER}\nPassword accepted. Test PASSES.\n{BORDER}"
            "\n\n".format(BORDER=border))

    @tags(type='positive', net='no')
    def test_update_server(self):
        """
        Creates a server and then updates the name, ipv4 and ipv6 values.

        Will call the create_active_server from server behaviors, then call
        update_server from cloudcafe's server_client passing in the newly
        created server's id, new random name, ipv4 address 192.168.32.16 and
        ipv6 address 3ffe:1900:4545:3:200:f8ff:fe21:67cf and then waiting for
        the server to make it to active status. Calling get_server to validate
        the updates occurred correctly

        The following assertions occur:
            - Server name was updated with new random name.
            - Server's IPV4 address is 192.168.32.16.
            - Server's IPV6 address is 3ffe:1900:4545:3:200:f8ff:fe21:67cf.
            - Server's creation date is still the same as the original.
            - Server's updated date is not the same as the original.
        """

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
