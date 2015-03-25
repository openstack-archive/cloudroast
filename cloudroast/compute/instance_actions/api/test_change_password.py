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
from cloudcafe.compute.common.types import ComputeHypervisors, \
    InstanceAuthStrategies, NovaServerStatusTypes as ServerStates
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.KVM, ComputeHypervisors.QEMU,
                   ComputeHypervisors.IRONIC, ComputeHypervisors.LXC_LIBVIRT],
                   'Change password not supported in current configuration.')
class ChangeServerPasswordTests(object):

    @tags(type='smoke', net='no')
    def test_change_password_response(self):
        """
        The status code for a change password request should be 202

        Validate that the response for the change password request in the
        setup has a status code of 202.

        The following assertions occur:
            - The change password response status code is equal to 202
        """
        self.assertEqual(202, self.resp.status_code)

    @tags(type='smoke', net='yes')
    def test_can_log_in_with_new_password(self):
        """
        The admin user should be able to log in with the new password

        As the test user get the details of the server created during test set
        up. Using the new_password value set during setup and the public IP
        address of the server get a remote instance client for the server.
        Validate that the remote client can authenticate to the server.

        The following assertions occur:
            - The attempt to authenticate to the server is successful
        """

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
            "Could not connect to server (%s) using new admin password %s" %
            (public_address, self.new_password))

    @tags(type='smoke', net='no')
    def test_password_changed_server_instance_actions(self):
        """
        Verify the correct actions are logged during a password change.

        Get the list of all actions that the server has taken from the Nova API.
        Filter the list so that only the actions 'changePassword' remain.
        Validate that the list of filtered actions has a length of 1 (that only
        1 changePassword action has been performed.) Validate that the values of
        the identified changePassword action match the values returned in the
        change password response received during test setup.

        The following assertions occur:
            - The list of actions that match 'changePassword' has only one item
            - The values for the changePassword action match the values received
              in response to the change password request
        """

        actions = self.servers_client.get_instance_actions(
            self.server.id).entity

        # Verify the change password action is listed
        self.assertTrue(any(a.action == 'changePassword' for a in actions))
        filtered_actions = [a for a in actions
                            if a.action == 'changePassword']
        self.assertEquals(len(filtered_actions), 1)

        password_action = filtered_actions[0]
        self.validate_instance_action(
            password_action, self.server.id, self.compute.user.user_id,
            self.compute.user.project_id,
            self.resp.headers['x-compute-request-id'])


class ChangePasswordBaseFixture(object):

    @classmethod
    def change_password(self):
        """
        Change password and wait for server to return to active state

        Change the password to a server to 'newslice129690TuG72Bgj2' and then
        wait for the server to return to state 'ACTIVE'.
        """

        self.new_password = "newslice129690TuG72Bgj2"
        self.resp = self.servers_client.change_password(
            self.server.id,
            self.new_password)
        self.server_behaviors.wait_for_server_status(
            self.server.id,
            ServerStates.ACTIVE)


class ServerFromImageChangePasswordTests(ServerFromImageFixture,
                                         ChangeServerPasswordTests,
                                         ChangePasswordBaseFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this setup:
            - A server with values from the test configuration

        The following actions are performed during this setup:
            - The password to the server is changed to "newslice129690TuG72Bgj2"
              using the 'change_password' method in the
              ChangePasswordBaseFixture class
        """
        super(ServerFromImageChangePasswordTests, cls).setUpClass()
        cls.create_server()
        cls.change_password()
