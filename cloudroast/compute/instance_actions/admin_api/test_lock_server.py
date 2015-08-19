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
from cloudcafe.compute.common.exceptions import ActionInProgress, BadRequest
from cloudcafe.compute.common.types import NovaServerRebootTypes

from cloudroast.compute.fixtures import ComputeAdminFixture


class LockServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are accessed from a parent class:
            - An instance from LockServerTests.

        The following resources are created during this setup:
            - Create a server from server behaviors.
            - Locks the same server in setup.

        """
        super(LockServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.admin_servers_client.lock_server(cls.server.id)

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that allow for the cleanup of any generated resources.

        The following resources are deleted during this tear down:
            - The server locked in setup is now unlocked.
        """
        super(LockServerTests, cls).tearDownClass()
        cls.admin_servers_client.unlock_server(cls.server.id)

    @tags(type='smoke', net='no')
    def test_cannot_delete_locked_server(self):
        """
        Verify that a locked server cannot be deleted

        Validate that the server can not be deleted when it is in a locked state.

        The following assertions occur:
            - The delete server request raises a 'Action In Progress'
              error when given a server id that is in a locked state.
        """

        with self.assertRaises(ActionInProgress):
            self.servers_client.delete_server(self.server.id)

    @tags(type='smoke', net='no')
    def test_cannot_change_password_of_locked_server(self):
        """
        Verify that the password of a locked server cannot be changed.

        Validate that the server can not change the password using the
        server id as the parameter.

        The following assertions occur:
            - The change server password request raises a 'Bad Request'
              error when given a server id that is in a locked state.
        """

        with self.assertRaises(ActionInProgress):
            self.servers_client.change_password(self.server.id,
                                                '123abcABC!!')

    @tags(type='smoke', net='no')
    def test_cannot_reboot_locked_server(self):
        """
        Verify that a locked server cannot be rebooted.

        Validate that the server can not be rebooted using the
        soft nova server reboot type.

        The following assertions occur:
            - The change server password request raises a 'Bad Request'
              error when given a server id that is in a locked state.
        """

        with self.assertRaises(ActionInProgress):
            self.servers_client.reboot(self.server.id,
                                       NovaServerRebootTypes.SOFT)

    @tags(type='smoke', net='no')
    def test_cannot_rebuild_locked_server(self):
        """
        Verify that a locked server cannot be rebuilt.

        Validate that the server can not be rebuilt with the same image
        as the original.

        The following assertions occur:
            - The rebuild server request raises a 'Action In Progress'
              error when given a server id that is in a locked state.
        """

        with self.assertRaises(ActionInProgress):
            self.servers_client.rebuild(self.server.id, self.image_ref)

    @tags(type='smoke', net='no')
    def test_cannot_resize_locked_server(self):
        """
        Verify that a locked server cannot be resized.

        Validate that the server can not be resized with the same flavor
        as the original.

        The following assertions occur:
            - The resize server request raises a 'Action In Progress'
              error when given a server id that is in a locked state.
        """

        with self.assertRaises(ActionInProgress):
            self.servers_client.resize(self.server.id, self.flavor_ref)
