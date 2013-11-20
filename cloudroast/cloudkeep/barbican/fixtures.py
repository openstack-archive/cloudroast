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
from os import path
from uuid import uuid4

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.cloudkeep.barbican.version.client import VersionClient
from cloudcafe.cloudkeep.barbican.secrets.client import SecretsClient
from cloudcafe.cloudkeep.barbican.orders.client import OrdersClient
from cloudcafe.cloudkeep.barbican.secrets.behaviors import SecretsBehaviors
from cloudcafe.cloudkeep.barbican.orders.behaviors import OrdersBehavior
from cloudcafe.cloudkeep.config import (MarshallingConfig, CloudKeepConfig,
                                        CloudKeepSecretsConfig,
                                        CloudKeepOrdersConfig)
from cloudcafe.common.tools import randomstring
from cloudcafe.identity.config import IdentityTokenConfig
from cloudcafe.identity.v2_0.tokens_api.behaviors import TokenAPI_Behaviors
from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client


class BarbicanFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls, keystone_config=None):
        super(BarbicanFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.cloudkeep = CloudKeepConfig()
        cls.keystone = keystone_config or IdentityTokenConfig()

    def get_id(self, request):
        """
        Helper function to extract the producer id from location header
        """
        self.assertEqual(request.status_code, 201, 'Invalid response code')
        location = request.headers.get('location')
        extracted_id = int(path.split(location)[1])
        return extracted_id

    def _check_for_duplicates(self, group1, group2):
        """Checks for duplicated entities between two lists
        of secrets/orders."""
        duplicates = [entity for entity in group1 if entity in group2]
        self.assertEqual(len(duplicates), 0,
                         'Lists of entities did not return unique entities')


class AuthenticationFixture(BarbicanFixture):

    @classmethod
    def _build_editable_keystone_config(cls):
        loaded_config = IdentityTokenConfig()
        # This is far from ideal, but I need to be able to edit the config
        config = type('SpoofedConfig', (object,), {
            'version': loaded_config.version,
            'username': loaded_config.username,
            'password': loaded_config.password,
            'tenant_name': loaded_config.tenant_name,
            'authentication_endpoint': loaded_config.authentication_endpoint})
        return config

    @classmethod
    def setUpClass(cls, keystone_config=None):
        super(AuthenticationFixture, cls).setUpClass(keystone_config)
        cls.auth_client = TokenAPI_Client(
            url=cls.keystone.authentication_endpoint,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.auth_behaviors = TokenAPI_Behaviors(cls.auth_client)

        # Get token and setup default_headers
        access = cls.auth_behaviors.get_access_data(
            username=cls.keystone.username,
            password=cls.keystone.password,
            tenant_name=cls.keystone.tenant_name)

        cls.token = access.token.id_ if access else None
        cls.tenant_id = access.token.tenant.id_ if access else None

        cls.version_client = VersionClient(
            url=cls.cloudkeep.base_url,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)


class VersionFixture(AuthenticationFixture):

    @classmethod
    def setUpClass(cls):
        super(VersionFixture, cls).setUpClass()
        cls.client = VersionClient(
            url=cls.cloudkeep.base_url,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)


class SecretsFixture(AuthenticationFixture):

    @classmethod
    def setUpClass(cls, keystone_config=None):
        super(SecretsFixture, cls).setUpClass(keystone_config)
        cls.config = CloudKeepSecretsConfig()
        cls.client = SecretsClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            tenant_id=cls.tenant_id or cls.cloudkeep.tenant_id,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.behaviors = SecretsBehaviors(client=cls.client, config=cls.config)

    def _check_list_of_secrets(self, resp, limit):
        """Checks that the response from getting list of secrets
        returns a 200 status code and the correct number of secrets.
        Also returns the list of secrets from the response.
        """
        self.assertEqual(resp.status_code, 200,
                         'Returned unexpected response code')
        sec_group = resp.entity
        self.assertEqual(len(sec_group.secrets), limit,
                         'Returned wrong number of secrets')
        return sec_group

    def tearDown(self):
        self.behaviors.delete_all_created_secrets()
        super(SecretsFixture, self).tearDown()


class SecretsPagingFixture(SecretsFixture):

    @classmethod
    def setUpClass(cls):
        super(SecretsPagingFixture, cls).setUpClass()
        for count in range(150):
            cls.behaviors.create_secret_from_config(use_expiration=False)

    def tearDown(self):
        """ Overrides superclass method so that secrets are not deleted
        between tests.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        cls.behaviors.delete_all_created_secrets()
        super(SecretsPagingFixture, cls).tearDownClass()


class OrdersFixture(AuthenticationFixture):
    @classmethod
    def setUpClass(cls, keystone_config=None):
        super(OrdersFixture, cls).setUpClass(keystone_config)
        cls.config = CloudKeepOrdersConfig()
        cls.orders_client = OrdersClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            tenant_id=cls.tenant_id or cls.cloudkeep.tenant_id,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.secrets_client = SecretsClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            tenant_id=cls.tenant_id or cls.cloudkeep.tenant_id,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.behaviors = OrdersBehavior(orders_client=cls.orders_client,
                                       secrets_client=cls.secrets_client,
                                       config=cls.config)

    def _check_list_of_orders(self, resp, limit):
        """Checks that the response from getting list of orders
        returns a 200 status code and the correct number of orders.
        Also returns the list of orders from the response.
        """
        self.assertEqual(resp.status_code, 200,
                         'Returned unexpected response code')
        ord_group = resp.entity
        self.assertEqual(len(ord_group.orders), limit,
                         'Returned wrong number of orders')
        return ord_group

    def tearDown(self):
        self.behaviors.delete_all_created_orders_and_secrets()
        super(OrdersFixture, self).tearDown()


class OrdersPagingFixture(OrdersFixture):

    @classmethod
    def setUpClass(cls):
        super(OrdersPagingFixture, cls).setUpClass()
        for count in range(150):
            cls.behaviors.create_order_from_config(use_expiration=False)

    def tearDown(self):
        """ Overrides superclass method so that orders are not deleted
        between tests.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        cls.behaviors.delete_all_created_orders_and_secrets()
        super(OrdersPagingFixture, cls).tearDownClass()


class BitLengthDataSetPositive(DatasetList):
    def __init__(self):
        self.append_new_dataset('192', {'bit_length': 192})
        self.append_new_dataset('128', {'bit_length': 128})
        self.append_new_dataset('256', {'bit_length': 256})


class BitLengthDataSetNegative(DatasetList):
    def __init__(self):
        large_string = str(bytearray().zfill(10001))

        self.append_new_dataset('invalid', {'bit_length': 'not-an-int'})
        self.append_new_dataset('negative', {'bit_length': -1})
        self.append_new_dataset('large_string', {'bit_length': large_string})


class NameDataSetPositive(DatasetList):
    def __init__(self):
        alphanumeric = randomstring.get_random_string(prefix='1a2b')
        random255 = randomstring.get_random_string(size=255)
        punctuation = '~!@#$%^&*()_+`-={}[]|:;<>,.?"'
        uuid = str(uuid4())

        self.append_new_dataset('alphanumeric', {'name': alphanumeric})
        self.append_new_dataset('punctuation', {'name': punctuation})
        self.append_new_dataset('len_255', {'name': random255})
        self.append_new_dataset('uuid', {'name': uuid})


class PayloadDataSetNegative(DatasetList):
    def __init__(self):
        self.append_new_dataset('empty', {'payload': ''})
        self.append_new_dataset('array', {'payload': ['boom']})
        self.append_new_dataset('int', {'payload': 123})


class ContentTypeEncodingDataSetTextPositive(DatasetList):
    def __init__(self):

        self.append_new_dataset(
            'text_plain',
            {'payload_content_type': 'text/plain',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'text_caps_plain',
            {'payload_content_type': 'TEXT/plain',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'text_plain_trailing_space',
            {'payload_content_type': 'text/plain ',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'text_plain_charset_utf8',
            {'payload_content_type': 'text/plain; charset=utf-8',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'text_plain_no_space_charset_utf8',
            {'payload_content_type': 'text/plain;charset=utf-8',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'text_plain_space_charset_utf8_trailing_space',
            {'payload_content_type': 'text/plain; charset=utf-8 ',
             'payload_content_encoding': None})


class ContentTypeEncodingDataSetBase64Positive(DatasetList):
    def __init__(self):

        self.append_new_dataset(
            'application_octet_stream',
            {'payload_content_type': 'application/octet-stream',
             'payload_content_encoding': 'base64'})


class ContentTypeEncodingDataSetNegative(DatasetList):
    def __init__(self):
        large_string = str(bytearray().zfill(10001))

        self.append_new_dataset(
            'empty_type_and_encoding',
            {'payload_content_type': '',
             'payload_content_encoding': ''})
        self.append_new_dataset(
            'null_type_and_encoding',
            {'payload_content_type': None,
             'payload_content_encoding': None})
        self.append_new_dataset(
            'large_string_type_and_encoding',
            {'payload_content_type': large_string,
             'payload_content_encoding': large_string})
        self.append_new_dataset(
            'int_type_and_encoding',
            {'payload_content_type': 123,
             'payload_content_encoding': 123})
        self.append_new_dataset(
            'base64_only',
            {'payload_content_type': None,
             'payload_content_encoding': 'base64'})
        self.append_new_dataset(
            'text_plain_and_empty_content_type',
            {'payload_content_type': 'text/plain',
             'payload_content_encoding': ''})
        self.append_new_dataset(
            'text_with_no_subtype',
            {'payload_content_type': 'text',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'text_slash_with_no_subtype',
            {'payload_content_type': 'text/',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'text_plain_and_space_content_type',
            {'payload_content_type': 'text/plain',
             'payload_content_encoding': ' '})
        self.append_new_dataset(
            'text_plain_and_spaces_content_type',
            {'payload_content_type': 'text/plain',
             'payload_content_encoding': '   '})
        self.append_new_dataset(
            'text_plain_and_base64',
            {'payload_content_type': 'text/plain',
             'payload_content_encoding': 'base64'})
        self.append_new_dataset(
            'text_plain_space_charset_utf88',
            {'payload_content_type': 'text/plain; charset=utf-88',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'invalid_and_base64',
            {'payload_content_type': 'invalid',
             'payload_content_encoding': 'base64'})
        self.append_new_dataset(
            'invalid_content_type',
            {'payload_content_type': 'invalid',
             'payload_content_encoding': None})
        self.append_new_dataset(
            'app_oct_and_invalid_encoding',
            {'payload_content_type': 'application/octet-stream',
             'payload_content_encoding': 'invalid'})
        self.append_new_dataset(
            'text_plain_and_invalid_encoding',
            {'payload_content_type': 'text/plain',
             'payload_content_encoding': 'invalid'})
        self.append_new_dataset(
            'invalid_encoding',
            {'payload_content_type': None,
             'payload_content_encoding': 'invalid'})
