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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudcafe.compute.common.types import NovaServerRebootTypes
from cloudcafe.compute.common.exceptions import Unauthorized
from cloudroast.compute.fixtures import ComputeFixture


class TokenRequiredTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates an active server.
            - Creates an image and waits for active status.
        """
        super(TokenRequiredTests, cls).setUpClass()
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.server = cls.server_behaviors.create_active_server(
            metadata=cls.metadata).entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

        image_name = rand_name('testimage')
        cls.image_meta = {'user_key1': 'value1', 'user_key2': 'value2'}
        image_resp = cls.servers_client.create_image(cls.server.id,
                                                     image_name,
                                                     cls.image_meta)
        assert image_resp.status_code == 202
        cls.image_id = cls.parse_image_id(image_resp)
        cls.image_behaviors.wait_for_image_status(
            cls.image_id, NovaImageStatusTypes.ACTIVE)
        cls.resources.add(cls.image_id, cls.images_client.delete_image)
        cls.auth_token = {'headers': {'X-Auth-Token': None}}

    @tags(type='negative', net='no')
    def test_list_flavors_with_invalid_token(self):
        """
        A list flavors request should fail.

        Will call list flavors expecting a "Unauthorized" exception to be
        raise because the call is being executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.flavors_client.list_flavors(
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_with_invalid_token(self):
        """
        A list flavors with detail call should fail.

        Will call list flavors with details expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.flavors_client.list_flavors_with_detail(
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_get_flavor_with_invalid_token(self):
        """
        A get flavor detail call should fail.

        Will call get flavor details expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.flavors_client.get_flavor_details(
                self.flavor_ref,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_images_with_invalid_token(self):
        """
        A list images call should fail.

        Will call list images expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.list_images(
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_images_detailed_with_invalid_token(self):
        """
        A list images with detail call should fail.

        Will call list images with details expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.list_images_with_detail(
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_get_image_with_invalid_token(self):
        """
        A get image call should fail.

        Will call get image expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.get_image(
                self.image_ref,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_delete_image_with_invalid_token(self):
        """
        A delete image call should fail.

        Will call delete image expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.delete_image(
                self.image_id,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_servers_with_invalid_token(self):
        """
        A list servers call should fail.

        Will call list servers expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.list_servers(
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_servers_detailed_with_invalid_token(self):
        """
        A list servers with detail call should fail.

        Will call list server with details expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.list_servers_with_detail(
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_server_addresses_with_invalid_token(self):
        """
        A list addresses call should fail.

        Will call list addresses expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.list_addresses(
                self.server.id, requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_server_addresses_by_network_with_invalid_token(self):
        """
        A list addresses by network call should fail.

        Will call list addresses by network expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.list_addresses_by_network(
                self.server.id, 'prviate', requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_create_server_with_invalid_token(self):
        """
        A create server call should fail.

        Will call create server expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.create_server(
                'test', self.image_ref, self.flavor_ref,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_get_server_unauthorized(self):
        """
        A get server call should fail.

        Will call get server expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.get_server(
                self.server.id,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_delete_server_with_invalid_token(self):
        """
        A delete server call should fail.

        Will call delete server expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.delete_server(
                self.server.id,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_change_server_password_with_invalid_token(self):
        """
        A change server password call should fail.

        Will call change password expecting a "Unauthorized"
        exception to be raise because the call is being executed without
        an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.change_password(
                self.server.id, 'newP@ssw0rd',
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_reboot_server_with_invalid_token(self):
        """
        A soft reboot server call should fail.

        Will call reboot server with the type of "SOFT" expecting a
        "Unauthorized" exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.reboot(
                self.server.id, NovaServerRebootTypes.SOFT,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_rebuild_server_with_invalid_token(self):
        """
        A rebuild server call should fail.

        Will call rebuild server expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.rebuild(
                self.server.id, self.image_ref_alt,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_resize_server_with_invalid_token(self):
        """
        A resize server call should fail.

        Will call resize server expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.resize(
                self.server.id, self.flavor_ref_alt,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_create_image_with_invalid_token(self):
        """
        A create image call should fail.

        Will call create image expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.create_image(
                self.server.id, 'testimage',
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_server_metadata_with_invalid_token(self):
        """
        A list server metadata call should fail.

        Will call list server metadata expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.list_server_metadata(
                self.server.id,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_set_server_metadata_with_invalid_token(self):
        """
        A set server metadata call should fail.

        Will call set server metadata expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            new_meta = {'meta2': 'data2', 'meta3': 'data3'}
            self.servers_client.set_server_metadata(
                self.server.id, new_meta,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_update_server_metadata_with_invalid_token(self):
        """
        A update server metadata call should fail.

        Will call update server metadata expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            new_meta = {'meta2': 'data2', 'meta3': 'data3'}
            self.servers_client.update_server_metadata(
                self.server.id, new_meta,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_get_server_metadata_item_with_invalid_token(self):
        """
        A get server metadata item call should fail.

        Will call get server metadata item expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.get_server_metadata_item(
                self.server.id, 'meta_key_1',
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_delete_server_metadata_item_with_invalid_token(self):
        """
        A delete server metadata item call should fail.

        Will call delete server metadata item expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.delete_server_metadata_item(
                self.server.id, 'meta_key_1',
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_set_server_metadata_item_with_invalid_token(self):
        """
        A set server metadata item call should fail.

        Will call set server metadata item expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.servers_client.set_server_metadata_item(
                self.server.id, 'meta_key_1', 'newvalue',
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_list_image_metadata_with_invalid_token(self):
        """
        A list image metadata call should fail.

        Will call list image metadata expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.list_image_metadata(
                self.image_id,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_set_image_metadata_with_invalid_token(self):
        """
        A set image metadata call should fail.

        Will call set image metadata expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            new_meta = {'user_meta2': 'data2', 'user_meta3': 'data3'}
            self.images_client.set_image_metadata(
                self.image_id, new_meta,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_update_image_metadata_with_invalid_token(self):
        """
        A update image metadata call should fail.

        Will call update image metadata expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            new_meta = {'user_meta2': 'data2', 'user_meta3': 'data3'}
            self.images_client.update_image_metadata(
                self.image_id, new_meta,
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_get_image_metadata_item_with_invalid_token(self):
        """
        A get image metadata item call should fail.

        Will call get image metadata item expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.get_image_metadata_item(
                self.image_id, 'user_key1',
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_delete_image_metadata_item_with_invalid_token(self):
        """
        A delete image metadata item call should fail.

        Will call delete image metadata item expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.delete_image_metadata_item(
                self.image_id, 'user_key1',
                requestslib_kwargs=self.auth_token)

    @tags(type='negative', net='no')
    def test_set_image_metadata_item_with_invalid_token(self):
        """
        A set image metadata item call should fail.

        Will call set image metadata item expecting a "Unauthorized"
        exception to be raise because the call is being
        executed without an auth token header.

        The following assertions occur:
            - Expecting a Unauthorized exception to be raised.
        """
        with self.assertRaises(Unauthorized):
            self.images_client.set_image_metadata_item(
                self.image_id, 'user_key1', 'newvalue',
                requestslib_kwargs=self.auth_token)


class InvalidTokenTests(TokenRequiredTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Sets invalidate auth token header.
        """
        super(InvalidTokenTests, cls).setUpClass()
        cls.auth_token = {'headers': {'X-Auth-Token': 'abc'}}

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that allow for the cleanup of any generated resources

        The following resources are deleted during this tear down:
            - The super class's tear down is called.
        """
        super(InvalidTokenTests, cls).tearDownClass()
