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
import base64
from datetime import datetime, timedelta
from os import path
from requests.exceptions import MissingSchema
from time import sleep, strftime

from barbicanclient.client import HTTPClientError as ClientException
from cafe.drivers.unittest.decorators import tags
from cafe.drivers.unittest.decorators import DataDrivenFixture
from cafe.drivers.unittest.decorators import data_driven_test
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.issue import skip_open_issue
from cloudcafe.cloudkeep.common.states import SecretsStates
from cloudroast.cloudkeep.client_lib.fixtures import (SecretsFixture,
                                                      SecretsPagingFixture)


class BlankNameDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('null', {'name': None})
        self.append_new_dataset('empty', {'name': ''})


class ValidNameDataset(BlankNameDataset):
    pass


class InvalidNameDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('numeric_positive', {'name': 80})
        self.append_new_dataset('numeric_zero', {'name': 0})
        self.append_new_dataset('numeric_negative', {'name': -80})


class ValidAlgorithmDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('unknown', {'algorithm': 'unknown'})
        self.append_new_dataset('aes', {'algorithm': 'aes'})


class InvalidAlgorithmDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('numeric_positive', {'algorithm': 80})
        self.append_new_dataset('numeric_zero', {'algorithm': 0})
        self.append_new_dataset('numeric_negative', {'algorithm': -80})


class ValidModeDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('unknown', {'mode': 'unknown'})
        self.append_new_dataset('cbc', {'mode': 'cbc'})


class InvalidModeDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset('numeric_positive', {'mode': 80})
        self.append_new_dataset('numeric_zero', {'mode': 0})
        self.append_new_dataset('numeric_negative', {'mode': -80})


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


class InvalidContentTypeDataset(DatasetList):
    def __init__(self):
        self.append_new_dataset(
            'text_plane', {'content_type': 'text/plane'})


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

    @tags(type='negative')
    @data_driven_test(InvalidNameDataset())
    def ddtest_create_secret_w_invalid_name(self, name):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          name=name)

    @tags(type='positive')
    @data_driven_test(ValidAlgorithmDataset())
    def ddtest_create_secret_w_valid_algorithm(self, algorithm):
        secret_ref = self.cl_behaviors.create_secret(algorithm=algorithm)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

    @tags(type='negative')
    @data_driven_test(InvalidAlgorithmDataset())
    def ddtest_create_secret_w_invalid_algorithm(self, algorithm):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          algorithm=algorithm)

    @tags(type='positive')
    @data_driven_test(ValidModeDataset())
    def ddtest_create_secret_w_valid_mode(self, mode):
        secret_ref = self.cl_behaviors.create_secret(mode=mode)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

    @tags(type='negative')
    @data_driven_test(InvalidModeDataset())
    def ddtest_create_secret_w_invalid_mode(self, mode):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          mode=mode)

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

    @tags(type='positive')
    def test_secret_with_payload_deletion(self):
        """ Covers case where the system fails to delete a secret if it
        contains a set "payload" field.
        """
        secret_ref = self.cl_behaviors.create_secret(
            payload='test', payload_content_type='text/plain')

        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        del_resp = self.cl_behaviors.delete_secret(secret_ref)
        self.assertIsNone(del_resp)

        deleted_secret = self.cl_behaviors.find_secret(secret_ref)
        self.assertIsNone(deleted_secret)

    @tags(type='positive')
    def test_creating_w_null_entries(self):
        """ Covers case where the system fails to delete a secret if it
        contains a set "payload" field.
        """
        secret_ref = self.cl_behaviors.create_secret()

        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

    @tags(type='negative')
    def test_creating_w_empty_entries(self):
        """ Covers case of creating a secret with empty Strings for all
        entries. Should return error.
        """
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          name='', expiration='', algorithm='', bit_length='',
                          mode='', payload='', payload_content_type='',
                          payload_content_encoding='')

    @tags(type='negative')
    def test_creating_w_oversized_secret(self):
        """ Covers creating a secret with a secret that is larger than
        the limit. Current size limit is 10k bytes. Beyond that,
        it should raise an exception.
        """
        data = bytearray().zfill(10001)
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          payload=str(data))

    @tags(type='negative')
    @data_driven_test(InvalidContentTypeDataset())
    def ddtest_create_secret_w_invalid_content_type(self, content_type):
        """ Covers creating secret with invalid content types.
        """
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          payload_content_type=content_type)

    @skip_open_issue('launchpad', '1276210')
    @tags(type='positive')
    def test_create_secret_w_valid_content_type_text(self):
        """ Covers creating secret with text/plain content type."""
        content_type = 'text/plain'
        secret_ref = self.cl_behaviors.create_secret(
            payload_content_type=content_type)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertIsNotNone(secret.content_types)

    @skip_open_issue('launchpad', '1276210')
    @tags(type='positive')
    def test_create_secret_w_valid_content_type_text_and_charset(self):
        """ Covers creating secret with text/plain including charset
        content type.
        """
        content_type = 'text/plain; charset=utf-8'
        secret_ref = self.cl_behaviors.create_secret(
            payload_content_type=content_type)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertIsNotNone(secret.content_types)

    @tags(type='negative')
    def test_creating_secret_w_invalid_expiration(self):
        """ Covers creating secret with expiration that has already passed.
        """
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret_overriding_cfg,
                          expiration='2000-01-10T14:58:52.546795')

    @skip_open_issue('launchpad', '1276210')
    @tags(type='positive')
    def test_creating_secret_w_only_content_type(self):
        """ Covers creating secret with only content type and no payload.
        """
        content_type = 'text/plain'
        secret_ref = self.cl_behaviors.create_secret(
            payload_content_type=content_type)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertIsNotNone(secret.content_types)
        self.assertEqual(secret.content_types.get('default'), content_type)

    @tags(type='positive')
    def test_creating_secret_w_aes_algorithm(self):
        """ Covers creating secret with an aes algorithm."""
        algorithm = 'aes'
        secret_ref = self.cl_behaviors.create_secret_overriding_cfg(
            algorithm=algorithm)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertEqual(secret.algorithm, algorithm)

    @tags(type='positive')
    def test_creating_secret_w_cbc_mode(self):
        """ Covers creating secret with an cbc cipher type."""
        mode = 'cbc'
        secret_ref = self.cl_behaviors.create_secret_overriding_cfg(
            mode=mode)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertEqual(secret.mode, mode)

    @tags(type='positive')
    def test_creating_secret_w_app_octet_mime_type_and_base64(self):
        """Covers case of creating a secret with application/octet-stream
        content type and base64 encoding."""
        payload_content_type = 'application/octet-stream'
        payload_content_encoding = 'base64'
        payload = 'bazinga'
        secret_ref = self.cl_behaviors.create_secret(
            payload=base64.b64encode(payload),
            payload_content_type=payload_content_type,
            payload_content_encoding=payload_content_encoding)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertEqual(secret.content_types.get('default'),
                         payload_content_type)

        actual_payload = self.cl_client.get_raw_secret(secret_ref,
                                                       payload_content_type)
        self.assertEqual(payload, actual_payload)

    @tags(type='positive')
    def test_creating_secret_w_large_string_values(self):
        """Covers case of creating secret with large String values."""
        large_string = str(bytearray().zfill(10001))
        secret_ref = self.cl_behaviors.create_secret_overriding_cfg(
            name=large_string,
            algorithm=large_string,
            mode=large_string)
        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertEqual(secret.name, large_string)
        self.assertEqual(secret.algorithm, large_string)
        self.assertEqual(secret.mode, large_string)

    @tags(type='positive')
    def test_creating_secret_w_max_secret_size(self):
        """Covers case of creating secret with large String values."""
        large_string = str(bytearray().zfill(10000))
        content_type = 'text/plain'
        content_encoding = None
        secret_ref = self.cl_behaviors.create_secret(
            payload=large_string,
            payload_content_type=content_type,
            payload_content_encoding=content_encoding)

        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        secret = self.cl_client.get_secret(secret_ref)
        self.assertIsNotNone(secret)
        self.assertEqual(secret.content_types.get('default'),
                         content_type)

        actual_payload = self.cl_client.get_raw_secret(secret_ref,
                                                       content_type)
        self.assertEqual(large_string, actual_payload)

    @tags(type='positive')
    def test_create_secret_then_expire_then_check(self):
        """Covers case where you create a secret that will soon
         expire.  After it expires, check it and verify that it
         is no longer a valid secret.
         """

        # create a secret that expires in 2 minutes
        two_minutes_ahead = (datetime.today() + timedelta(minutes=2))
        my_timezone = strftime("%z")
        timestamp = '{time}{timezone}'.format(
            time=two_minutes_ahead,
            timezone=my_timezone)
        payload = 'bazinga'
        content_type = 'text/plain'
        secret_ref = self.cl_client.create_secret(
            payload=payload,
            payload_content_type=content_type,
            expiration=timestamp)

        self.assertIsNotNone(secret_ref)
        self.assertIn('http', secret_ref)

        # now get the secret - will be still valid
        actual_payload = self.cl_client.get_raw_secret(secret_ref,
                                                       content_type)
        self.assertEqual(actual_payload, payload)

        # now wait 3 minutes.  This will allow the expiration time (above) to
        # pass before attempting to get the raw secret.
        sleep(3 * 60)

        # now get the secret - should be invalid (expired)
        self.assertRaises(ClientException,
                          self.cl_client.get_raw_secret,
                          secret_ref,
                          content_type)


class SecretsPagingAPI(SecretsPagingFixture):

    @tags(type='positive')
    def test_list_secrets_limit_and_offset(self):
        # First set of secrets
        sec_group1 = self.cl_client.list_secrets(limit=10, offset=0)

        # Second set of secrets
        sec_group2 = self.cl_client.list_secrets(limit=10, offset=10)

        self._check_for_duplicates(group1=sec_group1, group2=sec_group2)
