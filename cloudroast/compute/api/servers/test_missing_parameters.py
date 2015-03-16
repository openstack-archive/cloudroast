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
        Perform actions that setup the necessary resources for testing create server with missing params

        The following resources are created/defined during the setup
            - Uses server behaviors to create active server
            - Adds server id to resources wit the function to delete_server
        """
        super(ServerMissingParameterTests, cls).setUpClass()
        server_response = cls.server_behaviors.create_active_server()
        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_create_server_without_name(self):
        """
        Will try to create a server passing a name of none and expecting a bad request error to be returned

        This will call the create_server through the cloudcafe's server client without a name parameter
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                None, self.image_ref, self.flavor_ref)

    @tags(type='negative', net='no')
    def test_create_server_without_image(self):
        """
        Will try to create a server passing an image of none and expecting a bad request error to be returned

        This will call the create_server through the cloudcafe's server client without a image parameter
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('test', None, self.flavor_ref)

    @tags(type='negative', net='no')
    def test_create_server_without_flavor(self):
        """
        Will try to create a server passing a flavor of none and expecting a bad request error to be returned

        This will call the create_server through the cloudcafe's server client without a flavor parameter
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('test', self.image_ref, None)

    @tags(type='negative', net='no')
    def test_change_password_without_password(self):
        """
        Will try to change the password for a server passing in none and expecting a bad request error to be returned

        This will call the create_server through the cloudcafe's server client without a flavor parameter
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.change_password(self.server.id, None)

    @tags(type='negative', net='no')
    def test_reboot_server_without_type(self):
        """
        Will try to reboot the server with a type(soft or hard) of none

        This will call the reboot through the cloudcafe's server client wihtout a reboot type
        This will expect a BadRequest or ComputeFault or set fail with an exception message.
        No assertions are invoked
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
        Will try to resize a server passing a name of none and expecting a bad request error to be returned

        I really think its building it with an image ref.  This is expecting a bad request so it will pass no matter
        what.
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, None, self.image_ref)

    @tags(type='negative', net='no')
    def test_rebuild_server_without_image(self):
        """
        Will try to resize a server passing a image of none and expecting a bad request error to be returned

        I really think its building it with a name and an image of "test".
        This is expecting a bad request so it will pass no matter what.
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, 'test', None)

    @tags(type='negative', net='no')
    def test_resize_server_without_flavor(self):
        """
        Will try to resize a server passing a flavor of none and expecting a bad request error to be returned

        This will call the resize through the cloudcafe's server client without a flavor parameter
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.resize(self.server.id, None)

    @tags(type='negative', net='no')
    def test_create_image_without_name(self):
        """
        Will try to resize a server passing a name of none and expecting a bad request error to be returned

        This will call the create_image through the cloudcafe's server client without a name parameter
        The following assertions occur
            - Expecting the BadRequest Exception to be raised
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_image(self.server.id, None)
