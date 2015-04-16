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
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.compute.config import ComputeEndpointConfig, \
    ComputeAuthorizationConfig, UserAuthConfig
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudcafe.compute.common.types import NovaServerRebootTypes
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudcafe.compute.common.exception_handler import ExceptionHandler
from cloudcafe.compute.flavors_api.client import FlavorsClient
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.images_api.client import ImagesClient
from cloudroast.compute.fixtures import ComputeFixture


class AuthorizationTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates an active server with metadata.
            - Creates an image with metadata and waits for active status.
        """
        super(AuthorizationTests, cls).setUpClass()
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

        secondary_user = ComputeAuthorizationConfig()
        compute_endpoint = ComputeEndpointConfig()
        auth_endpoint_config = UserAuthConfig()
        access_data = AuthProvider.get_access_data(
            auth_endpoint_config, secondary_user)

        compute_service = access_data.get_service(
            compute_endpoint.compute_endpoint_name)
        url = compute_service.get_endpoint(
            compute_endpoint.region).public_url

        cls.flavors_client = FlavorsClient(
            url, access_data.token.id_, 'json', 'json')
        cls.servers_client = ServersClient(
            url, access_data.token.id_, 'json', 'json')
        cls.images_client = ImagesClient(
            url, access_data.token.id_, 'json', 'json')
        cls.flavors_client.add_exception_handler(ExceptionHandler())

    @tags(type='negative', net='no')
    def test_get_image_unauthorized(self):
        """
        A get image request should fail when not authorized.

        Will call get image expecting a "ItemNotFound" exception to be
        raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image(self.image_id)

    @tags(type='negative', net='no')
    def test_delete_image_unauthorized(self):
        """
        A delete image request should fail when not authorized.

        Will call delete image expecting a "ItemNotFound" exception to be
        raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(self.image_id)

    @tags(type='negative', net='no')
    def test_get_server_unauthorized(self):
        """
        A get server request should fail when not authorized.

        Will call get server expecting a "ItemNotFound" exception to be
        raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(self.server.id)

    @tags(type='negative', net='no')
    def test_list_server_addresses_with_invalid_token(self):
        """
        A list addresses request should fail when not authorized.

        Will call list addresses expecting a "ItemNotFound" exception to be
        raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.list_addresses(
                self.server.id)

    @tags(type='negative', net='no')
    def test_list_server_addresses_by_network_with_invalid_token(self):
        """
        A list addresses by network request should fail when not authorized.

        Will call list address by network expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.list_addresses_by_network(
                self.server.id, 'prviate')

    @tags(type='negative', net='no')
    def test_delete_server_unauthorized(self):
        """
        A delete server request should fail when not authorized.

        Will call delete server expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server(self.server.id)

    @tags(type='negative', net='no')
    def test_change_server_password_unauthorized(self):
        """
        A change password request should fail when not authorized.

        Will call change password expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.change_password(self.server.id, 'newP@ssw0rd')

    @tags(type='negative', net='no')
    def test_reboot_server_unauthorized(self):
        """
        A soft reboot request should fail when not authorized.

        Will call reboot server expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.reboot(self.server.id,
                                       NovaServerRebootTypes.SOFT)

    @tags(type='negative', net='no')
    def test_rebuild_server_unauthorized(self):
        """
        A rebuild request should fail when not authorized.

        Will call rebuild server expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.rebuild(self.server.id, self.image_ref_alt)

    @tags(type='negative', net='no')
    def test_resize_server_unauthorized(self):
        """
        A resize request should fail when not authorized.

        Will call resize server expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.resize(self.server.id, self.flavor_ref_alt)

    @tags(type='negative', net='no')
    def test_create_image_unauthorized(self):
        """
        A create image request should fail when not authorized.

        Will call create image expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.create_image(self.server.id, 'testimage')

    @tags(type='negative', net='no')
    def test_list_server_metadata_unauthorized(self):
        """
        A list server metadata request should fail when not authorized.

        Will call list server metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.list_server_metadata(self.server.id)

    @tags(type='negative', net='no')
    def test_set_server_metadata_unauthorized(self):
        """
        A set server metadata request should fail when not authorized.

        Will call set server metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            new_meta = {'meta2': 'data2', 'meta3': 'data3'}
            self.servers_client.set_server_metadata(self.server.id, new_meta)

    @tags(type='negative', net='no')
    def test_update_server_metadata_unauthorized(self):
        """
        A update server metadata request should fail when not authorized.

        Will call update server metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            new_meta = {'meta2': 'data2', 'meta3': 'data3'}
            self.servers_client.update_server_metadata(
                self.server.id, new_meta)

    @tags(type='negative', net='no')
    def test_get_server_metadata_item_unauthorized(self):
        """
        A get server metadata request should fail when not authorized.

        Will call get server metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server_metadata_item(
                self.server.id, 'meta_key_1')

    @tags(type='negative', net='no')
    def test_delete_server_metadata_item_unauthorized(self):
        """
        A delete server metadata request should fail when not authorized.

        Will call delete server metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server_metadata_item(
                self.server.id, 'meta_key_1')

    @tags(type='negative', net='no')
    def test_set_server_metadata_item_unauthorized(self):
        """
        A set server metadata item request should fail when not authorized.

        Will call set server metadata item expecting a "ItemNotFound"
        exception to be raised because the call is being executed with
        insufficient privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.set_server_metadata_item(
                self.server.id, 'meta_key_1', 'newvalue')

    @tags(type='negative', net='no')
    def test_list_image_metadata_unauthorized(self):
        """
        A list image metadata request should fail when not authorized.

        Will call list image metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.list_image_metadata(self.image_id)

    @tags(type='negative', net='no')
    def test_set_image_metadata_unauthorized(self):
        """
        A set image metadata request should fail when not authorized.

        Will call set image metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            new_meta = {'user_meta2': 'data2', 'user_meta3': 'data3'}
            self.images_client.set_image_metadata(self.image_id, new_meta)

    @tags(type='negative', net='no')
    def test_update_image_metadata_unauthorized(self):
        """
        A update image metadata request should fail when not authorized.

        Will call update image metadata expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            new_meta = {'user_meta2': 'data2', 'user_meta3': 'data3'}
            self.images_client.update_image_metadata(self.image_id, new_meta)

    @tags(type='negative', net='no')
    def test_get_image_metadata_item_unauthorized(self):
        """
        A get image metadata item request should fail when not authorized.

        Will call get image metadata item expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image_metadata_item(
                self.image_id, 'user_key1')

    @tags(type='negative', net='no')
    def test_delete_image_metadata_item_unauthorized(self):
        """
        A delete image metadata item request should fail when not authorized.

        Will call delete image metadata item expecting a "ItemNotFound"
        exception to be raised because the call is being executed with
        insufficient privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image_metadata_item(
                self.image_id, 'user_key1')

    @tags(type='negative', net='no')
    def test_set_image_metadata_item_unauthorized(self):
        """
        A set image metadata item request should fail when not authorized.

        Will call set image metadata item expecting a "ItemNotFound" exception
        to be raised because the call is being executed with insufficient
        privileges.

        The following assertions occur:
            - Expecting a ItemNotFound exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.set_image_metadata_item(
                self.image_id, 'user_key1', 'newvalue')