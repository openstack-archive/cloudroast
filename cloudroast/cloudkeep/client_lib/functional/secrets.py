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
from requests.exceptions import MissingSchema

from barbicanclient.client import HTTPClientError as ClientException
from cafe.drivers.unittest.decorators import tags
from cafe.drivers.unittest.decorators import DataDrivenFixture
from cafe.drivers.unittest.decorators import data_driven_test
from cafe.drivers.unittest.datasets import DatasetList
from cloudcafe.cloudkeep.common.states import SecretsStates
from cloudroast.cloudkeep.client_lib.fixtures import (SecretsFixture,
                                                      SecretsPagingFixture)


class BlankNameDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('null', {'name': None})
        self.append_new_dataset('empty', {'name': ''})


class ValidNameDataset(BlankNameDataset):
    pass


class InvalidPayloadDataset(DatasetList):
    def __init__(self):
        large_data = bytearray().zfill(10001)
        large_data = large_data.decode("utf-8")
        self.append_new_dataset('oversized', {'payload': large_data})
        self.append_new_dataset('array', {'payload': ['boom']})


class InvalidBitLengthDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('array', {'bit_len': ['boom']})
        self.append_new_dataset('str', {'bit_len': 'b'})
        #self.append_new_dataset('dict', {'bit_len': {}}) # Fails
        self.append_new_dataset('negative', {'bit_len': -1})


@DataDrivenFixture
class SecretsAPI(SecretsFixture):

    @tags(type='positive')
    def test_create_secret_w_payload_and_type(self):
        secret_ref = self.cl_behaviors.create_secret(
            payload='test', payload_content_type='text/plain')

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertEqual(secret.content_types.get('default'), 'text/plain')

    @tags(type='positive')
    @data_driven_test(ValidNameDataset())
    def ddtest_create_secret_w_name(self, name):
        secret_ref = self.cl_behaviors.create_secret(name=name)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

    @tags(type='positive')
    @data_driven_test(BlankNameDataset())
    def ddtest_verify_name_defaults_to_id_w(self, name):
        """ When a secret is passed in a blank name it defaults the
        name to the secret id.
        """
        secret_ref = self.cl_behaviors.create_secret(name=name)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        secret_id = path.split(secret_ref)[-1]
        self.assertEqual(secret.name, secret_id)

    @tags(type='negative')
    @data_driven_test(InvalidPayloadDataset())
    def ddtest_create_secret_w_invalid_payload(self, payload):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          payload=payload)

    @tags(type='negative')
    @data_driven_test(InvalidBitLengthDataset())
    def ddtest_create_secret_w_invalid_bit_length(self, bit_len):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret_overriding_cfg,
                          bit_length=bit_len)

    @tags(type='negative')
    def test_delete_nonexistent_secret(self):
        self.assertRaises(MissingSchema,
                          self.cl_client.delete_secret,
                          href='invalid-ref')

    @tags(type='negative')
    def test_get_nonexistent_secret(self):
        self.assertRaises(ValueError,
                          self.cl_client.get_secret,
                          href='invalid-ref')

    @tags(type='positive')
    def test_get_secret_metadata(self):
        resp = self.barb_behaviors.create_secret_from_config()
        secret_meta = self.cl_client.get_secret(href=resp.ref)

        self.assertIsNotNone(secret_meta)
        self.assertEqual(secret_meta.status, SecretsStates.ACTIVE)
        self.assertEqual(secret_meta.name, self.config.name)
        self.assertEqual(secret_meta.mode, self.config.mode)
        self.assertEqual(secret_meta.algorithm, self.config.algorithm)
        self.assertEqual(secret_meta.bit_length, self.config.bit_length)

    @tags(type='negative')
    def test_get_raw_secret_w_nonexistent_secret(self):
        self.assertRaises(MissingSchema,
                          self.cl_client.get_raw_secret,
                          href='not-an-href',
                          content_type='content-type')

    @tags(type='negative')
    def test_get_empty_raw_secret(self):
        resp = self.barb_behaviors.create_secret()
        self.assertEqual(resp.status_code, 201)

        self.assertRaises(ClientException,
                          self.cl_client.get_raw_secret,
                          href=resp.ref,
                          content_type='text/plain')

    @tags(type='negative')
    def test_get_raw_secret_w_invalid_content_type(self):
        resp = self.barb_behaviors.create_secret(
            payload='test', payload_content_type='text/plain')
        self.assertEqual(resp.status_code, 201)

        self.assertRaises(ClientException,
                          self.cl_client.get_raw_secret,
                          href=resp.ref,
                          content_type='crypto/boom')

    @tags(type='positive')
    def test_get_raw_secret_after_update(self):
        resp = self.barb_behaviors.create_secret()
        self.assertEqual(resp.status_code, 201)

        data = 'test_update_str'
        update_resp = self.barb_client.add_secret_payload(
            secret_id=resp.id,
            payload=data,
            payload_content_type=self.config.payload_content_type)
        self.assertEqual(update_resp.status_code, 200)

        raw_secret = self.cl_client.get_raw_secret(
            href=resp.ref,
            content_type=self.config.payload_content_type)
        self.assertEquals(raw_secret, data)


class SecretsPagingAPI(SecretsPagingFixture):

    @tags(type='positive')
    def test_list_secrets_limit_and_offset(self):
        # First set of secrets
        sec_group1 = self.cl_client.list_secrets(limit=10, offset=0)

        # Second set of secrets
        sec_group2 = self.cl_client.list_secrets(limit=10, offset=10)

        self._check_for_duplicates(group1=sec_group1, group2=sec_group2)
