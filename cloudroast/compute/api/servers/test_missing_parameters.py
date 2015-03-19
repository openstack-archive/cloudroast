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
from cloudcafe.compute.common.exceptions import BadRequest, ComputeFault
from cloudroast.compute.fixtures import ComputeFixture


class ServerMissingParameterTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are accessed from a parent class:
            - An instance from ComputeFixture

        The following resources are created during the setup:
            - Uses server behaviors to create active server.
            - Adds server id to resources with the function to delete_server.
        """
        super(ServerMissingParameterTests, cls).setUpClass()
        server_response = cls.server_behaviors.create_active_server()
        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_create_server_without_name(self):
        """
        Will try to create a server passing a name of none.

        This will call the create_server through the cloudcafe's server client
        without a name parameter.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                None, self.image_ref, self.flavor_ref)

    @tags(type='negative', net='no')
    def test_create_server_without_image(self):
        """
        Will try to create a server passing an image of none.

        This will call the create_server through the cloudcafe's server client
        without a image parameter.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('test', None, self.flavor_ref)

    @tags(type='negative', net='no')
    def test_create_server_without_flavor(self):
        """
        Will try to create a server passing a flavor of none.

        This will call the create_server through the cloudcafe's server client
        without a flavor parameter.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('test', self.image_ref, None)

    @tags(type='negative', net='no')
    def test_change_password_without_password(self):
        """
        Will try to change the password for a server passing in none.

        This will call the create_server through the cloudcafe's server client
        without a password parameter.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.change_password(self.server.id, None)

    @tags(type='negative', net='no')
    def test_reboot_server_without_type(self):
        """
        Will try to reboot the server with a type of none.

        This will call the reboot through cloudcafe's server client
        without a reboot type. This will expect a BadRequest or ComputeFault
        or set fail with an exception message.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised and caught.
        """
        try:
            self.servers_client.reboot(self.server.id, None)
        except (BadRequest, ComputeFault):
            # Raises ComputeFault in Havana or earlier, BadRequest after then
            pass
        else:
            self.fail(
                "Expected ComputeFault or BadRequest to be raised when "
                "reboot type parameter is excluded.")

    @tags(type='negative', net='no')
    def test_rebuild_server_without_name(self):
        """
        Will try to resize a server passing a name of none.

        This will call the rebuild through cloudcafe's server client
        without a name and expect a BadRequest to raised.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, None, self.image_ref)

    @tags(type='negative', net='no')
    def test_rebuild_server_without_image(self):
        """
        Will try to resize a server passing a image of none.

        This will call the rebuild through cloudcafe's server client
        without an image and expect a BadRequest to raised.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, 'test', None)

    @tags(type='negative', net='no')
    def test_resize_server_without_flavor(self):
        """
        Will try to resize a server passing a flavor of none.

        This will call the resize through the cloudcafe's server client
        without a flavor parameter.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.resize(self.server.id, None)

    @tags(type='negative', net='no')
    def test_create_image_without_name(self):
        """
        Will try to resize a server passing a name of none.

        This will call the create_image through the cloudcafe's server client
        without a name parameter.

        This test will be successful if:
            - Expecting the BadRequest Exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_image(self.server.id, None)
