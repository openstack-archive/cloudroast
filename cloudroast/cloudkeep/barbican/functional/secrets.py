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
import json
import re
import unittest
import unittest2
from datetime import datetime, timedelta
from sys import maxint
from time import sleep, strftime

from cloudroast.cloudkeep.barbican.fixtures import (
    SecretsFixture, SecretsPagingFixture, NameDataSetPositive,
    PayloadDataSetNegative, ContentTypeEncodingDataSetNegative,
    ContentTypeEncodingDataSetTextPositive,
    ContentTypeEncodingDataSetBase64Positive, ModeDataSetPositive,
    ModeDataSetNegative)
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.issue import skip_open_issue
from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)


class SecretBitLengthDataSetPositive(DatasetList):
    def __init__(self):
        self.append_new_dataset('one', {'bit_length': 1})
        self.append_new_dataset('seven', {'bit_length': 7})
        self.append_new_dataset('eight', {'bit_length': 8})
        self.append_new_dataset('fifteen', {'bit_length': 15})
        self.append_new_dataset('sixteen', {'bit_length': 16})
        self.append_new_dataset('512', {'bit_length': 512})
        self.append_new_dataset('large_int', {'bit_length': maxint})


class SecretBitLengthDataSetNegative(DatasetList):
    def __init__(self):
        large_string = str(bytearray().zfill(10001))

        self.append_new_dataset('invalid', {'bit_length': 'not-an-int'})
        self.append_new_dataset('empty', {'bit_length': ''})
        self.append_new_dataset('blank', {'bit_length': ' '})
        self.append_new_dataset('large_string', {'bit_length': large_string})
        self.append_new_dataset('negative_maxint', {'bit_length': -maxint - 1})
        self.append_new_dataset('negative_one', {'bit_length': -1})
        self.append_new_dataset('zero', {'bit_length': 0})


class SecretModeDataSetPositive(ModeDataSetPositive):
    def __init__(self):
        super(SecretModeDataSetPositive, self).__init__()
        large_string = str(bytearray().zfill(10001))
        self.append_new_dataset('large_string', {'mode': large_string})
        self.append_new_dataset('unknown-positive', {'mode': 'unknown'})


class SecretModeDataSetNegative(ModeDataSetNegative):
    pass


class SecretContentTypeDataSetNegative(ContentTypeEncodingDataSetNegative):
    def __init__(self):
        super(SecretContentTypeDataSetNegative, self).__init__()
        self.append_new_dataset(
            'app_oct_only',
            {'payload_content_type': 'application/octet-stream',
             'payload_content_encoding': None})


class SecretContentTypeDataSetTextPositive\
        (ContentTypeEncodingDataSetTextPositive):
    def __init__(self):
        super(SecretContentTypeDataSetTextPositive, self).__init__()

        # Removing for Bug #1252873
        excluded = ['text_plain_trailing_space',
                    'text_plain_space_charset_utf8_trailing_space',
                    'text_caps_plain']
        [self.remove(ds) for ds in list(self) if ds.name in excluded]


class SecretContentTypeDataSetBase64Positive\
        (ContentTypeEncodingDataSetBase64Positive):
    def __init__(self):
        super(SecretContentTypeDataSetBase64Positive, self).__init__()


@DataDrivenFixture
class DataDriveSecretsAPI(SecretsFixture):

    @data_driven_test(dataset_source=SecretBitLengthDataSetPositive())
    @tags(type='positive')
    def ddtest_creating_secret_w_bit_length(self, bit_length=None):
        """Covers cases of creating a secret with various bit lengths."""
        resps = self.behaviors.create_and_check_secret(bit_length=bit_length)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Creation failed with unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(resps.get_resp.status_code, 200,
                         'Retrieval failed with unexpected response code')
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, bit_length)

    @data_driven_test(dataset_source=SecretBitLengthDataSetNegative())
    @tags(type='negative')
    def ddtest_negative_creating_secret_w_bit_length(self, bit_length=None):
        """Covers cases of creating a secret with invalid bit lengths.
        Should return 400."""
        resp = self.behaviors.create_secret(bit_length=bit_length)
        self.assertEqual(resp.status_code, 400,
                         'Creation should have failed with 400')

    @data_driven_test(dataset_source=SecretModeDataSetPositive())
    @tags(type='positive')
    def ddtest_creating_secret_w_mode(self, mode=None):
        """Covers cases of creating a secret with various modes."""
        if len(mode) >= 10001:
            self._skip_on_issue('launchpad', '1335327')

        resps = self.behaviors.create_and_check_secret(mode=mode)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Creation failed with unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(resps.get_resp.status_code, 200,
                         'Retrieval failed with unexpected response code')
        self.assertEqual(secret.mode, mode)

    @data_driven_test(dataset_source=SecretModeDataSetNegative())
    @tags(type='negative')
    def ddtest_negative_creating_secret_w_mode(self, mode=None):
        """Covers cases of creating a secret with invalid modes.
        Should return 400.
        """
        resp = self.behaviors.create_secret(mode=mode)
        self.assertEqual(resp.status_code, 400,
                         'Creation should have failed with 400')

    @data_driven_test(dataset_source=NameDataSetPositive())
    @tags(type='positive')
    def ddtest_creating_secret_w_name(self, name=None):
        """Covers cases of creating secret with various names."""
        resps = self.behaviors.create_and_check_secret(name=name)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Creation failed with unexpected response code')
        secret = resps.get_resp.entity
        self.assertEqual(secret.name, name, 'Secret name is not correct')

    @data_driven_test(dataset_source=PayloadDataSetNegative())
    @tags(type='negative')
    def ddtest_creating_secret_w_payload(self, payload=None):
        """Covers creating secret with various payloads."""
        resp = self.behaviors.create_secret(
            payload_content_type=self.config.payload_content_type,
            payload_content_encoding=self.config.payload_content_encoding,
            payload=payload)
        self.assertEqual(resp.status_code, 400,
                         'Creation should have failed with 400')

    @data_driven_test(dataset_source=SecretContentTypeDataSetNegative())
    @tags(type='negative')
    def ddtest_creating_secret(self, payload_content_type=None,
                               payload_content_encoding=None):
        """Covers creating secret with various invalid/error combinations of
        content types and encodings."""
        resp = self.behaviors.create_secret(
            payload_content_type=payload_content_type,
            payload_content_encoding=payload_content_encoding,
            payload=self.config.payload)
        self.assertEqual(resp.status_code, 400,
                         'Creation should have failed with 400')

    @data_driven_test(dataset_source=SecretContentTypeDataSetTextPositive())
    @tags(type='positive')
    def ddtest_creating_secret_normalize_content_type_text(
            self,
            payload_content_type=None,
            payload_content_encoding=None):
        """Covers creating secret with various valid combinations of
        content types and encodings."""
        create_resp = self.behaviors.create_secret(
            payload_content_type=payload_content_type,
            payload_content_encoding=payload_content_encoding,
            payload=self.config.payload)
        self.assertEqual(create_resp.status_code, 201,
                         'Secret creation was not successful')

        get_resp = self.client.get_secret(
            create_resp.id,
            payload_content_type=payload_content_type,
            payload_content_encoding=payload_content_encoding)
        self.assertEqual(get_resp.content, self.config.payload,
                         'Secret creation succeeded but validation failed')

    @data_driven_test(dataset_source=SecretContentTypeDataSetBase64Positive())
    @tags(type='positive')
    def ddtest_creating_secret_normalize_content_type_b64(
            self,
            payload_content_type=None,
            payload_content_encoding=None):
        """Covers creating secret with various valid combinations of
        content types and encodings."""
        create_resp = self.behaviors.create_secret(
            payload_content_type=payload_content_type,
            payload_content_encoding=payload_content_encoding,
            payload=base64.b64encode(self.config.payload))
        self.assertEqual(create_resp.status_code, 201,
                         'Secret creation was not successful')

        get_resp = self.client.get_secret(
            create_resp.id,
            payload_content_type=payload_content_type,
            payload_content_encoding=payload_content_encoding)
        self.assertEqual(get_resp.content, self.config.payload,
                         'Secret creation succeeded but validation failed')


class SecretsAPI(SecretsFixture):

    def check_expiration_iso8601_timezone(self, timezone, offset):
        """Creates a secret with an expiration for the timezone and
        offset and checks that the creation succeeds and the expiration
        is correct."""
        one_day_ahead = (datetime.today() + timedelta(days=1))
        timestamp = '{time}{timezone}'.format(
            time=one_day_ahead,
            timezone=timezone)

        resp = self.behaviors.create_secret_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp.status_code, 201)

        secret = self.client.get_secret(resp.id).entity
        exp = datetime.strptime(secret.expiration, '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(exp, one_day_ahead + timedelta(hours=offset),
                         'Response didn\'t return the expected time')

    def check_invalid_expiration_timezone(self, timezone):
        """Creates a secret with an expiration for the given invalid
        timezone and checks that the creation fails.
        """
        timestamp = '{time}{timezone}'.format(
            time=(datetime.today() + timedelta(days=1)),
            timezone=timezone)

        resp = self.behaviors.create_secret_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp.status_code, 400)

    @tags(type='positive')
    @skip_open_issue('launchpad', '1311240')
    def test_secret_with_payload_deletion(self):
        """ Covers case where the system fails to delete a secret if it
        contains a set "payload" field.
        - Reported in Barbican GitHub Issue #77
        """
        resp = self.behaviors.create_secret_from_config(use_expiration=False,
                                                        use_payload=True)
        self.assertEqual(resp.status_code, 201)

        del_resp = self.behaviors.delete_secret(resp.id)
        self.assertEqual(del_resp.status_code, 204)

    @skip_open_issue('launchpad', '1321394')
    @tags(type='positive')
    def test_create_secret_with_long_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #131
        """
        self.check_expiration_iso8601_timezone('-05:00', 5)
        self.check_expiration_iso8601_timezone('+05:00', -5)

    @unittest2.skip('Issue #135')
    @tags(type='positive')
    def test_create_secret_with_short_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #135
        """
        self.check_expiration_iso8601_timezone('-01', 1)
        self.check_expiration_iso8601_timezone('+01', -1)

    @unittest2.skip('Issue #134')
    @tags(type='negative')
    def test_create_secret_with_bad_expiration_timezone(self):
        """ Covers case of a malformed timezone being added to the expiration.
        - Reported in Barbican GitHub Issue #134
        """
        self.check_invalid_expiration_timezone('-5:00')

    @tags(type='positive')
    def test_creating_w_null_entries(self):
        """ Covers case when you create a secret full of nulls. """
        resp = self.behaviors.create_secret()
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_creating_w_empty_entries(self):
        """ Covers case of creating a secret with empty Strings for all
        entries. Should return a 400.
        """
        resp = self.behaviors.create_secret(
            name='', expiration='', algorithm='', mode='',
            payload='', payload_content_type='', payload_content_encoding='')
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_w_empty_name_and_content_type_no_payload(self):
        """ When a test is created with an empty or null name attribute, the
         system should return the secret's UUID on a get
         - Reported in Barbican GitHub Issue #89
        """
        c_resp = self.behaviors.create_secret(
            name='', payload_content_type=self.config.payload_content_type)

        self.assertEqual(c_resp.status_code, 400,
                         'Should have failed with 400 since no payload sent')

    @tags(type='positive')
    def test_creating_w_empty_name(self):
        """ When a test is created with an empty or null name attribute, the
         system should return the secret's UUID on a get
         - Reported in Barbican GitHub Issue #89
        """
        c_resp = self.behaviors.create_secret(
            name='', payload=self.config.payload,
            payload_content_type=self.config.payload_content_type,
            payload_content_encoding=self.config.payload_content_encoding)

        get_resp = self.client.get_secret(secret_id=c_resp.id)
        self.assertEqual(get_resp.entity.name, c_resp.id,
                         'Name doesn\'t match UUID of secret')

    @tags(type='positive')
    def test_creating_w_null_name(self):
        """ When a test is created with an empty or null name attribute, the
         system should return the secret's UUID on a get
         - Reported in Barbican GitHub Issue #89
        """
        c_resp = self.behaviors.create_secret(name=None)
        get_resp = self.client.get_secret(secret_id=c_resp.id)
        self.assertEqual(get_resp.entity.name, c_resp.id,
                         'Name doesn\'t match UUID of secret')

    @tags(type='positive')
    def test_creating_w_none_as_bit_length(self):
        """ When a test is created with None for the bit length attribute, the
         system should successfully return the secret reference URI.
        """
        resp = self.behaviors.create_secret(bit_length=None)
        self.assertEqual(resp.status_code, 201,
                         'Unexpected return code from secret create with '
                         'None bit length')

    @tags(type='positive')
    def test_creating_w_none_as_bit_length_no_default(self):
        """ When a test is created with None for the bit length attribute, the
         system should successfully return the secret reference URI.
        """
        resp = self.behaviors.create_secret(bit_length=None)
        get_resp = self.client.get_secret(resp.id)
        self.assertEqual(get_resp.status_code, 200,
                         'Unexpected return code getting secret with '
                         'None bit length')
        self.assertEqual(get_resp.entity.bit_length, None,
                         'Bit length in secret should be None')

    @tags(type='negative')
    def test_creating_w_oversized_secret(self):
        """ Covers creating a secret with a secret that is larger than
        the max secret payload size. Should return a 413 if the secret
        size is greater than the maximum allowed size.
        """

        data = bytearray().zfill(
            self.cloudkeep.max_allowed_secret_in_bytes + 1)

        resps = self.behaviors.create_and_check_secret(payload=str(data))
        self.assertEqual(resps.create_resp.status_code, 413,
                         'Create should have failed with 413')

    @unittest.skip("Blueprint barbican-enforce-content-type")
    @tags(type='negative')
    def test_creating_w_invalid_content_type(self):
        """ Covers case of creating secret with an invalid content type in
        HTTP header.  Should return 415.
        """
        resp = self.behaviors.create_secret(
            headers={'Content-Type': 'crypto/boom'})
        self.assertEqual(resp.status_code, 415,
                         'Should have failed with 415')

    @tags(type='negative')
    def test_getting_secret_that_doesnt_exist(self):
        """Covers getting a nonexistent secret."""
        resp = self.client.get_secret('not_a_uuid')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    @tags(type='negative')
    def test_getting_secret_data_w_invalid_mime_type(self):
        """Covers getting a secret with an invalid mime type."""
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        resp = self.client.get_secret(resp.id, payload_content_type='i/m')
        self.assertEqual(resp.status_code, 406, 'Should have failed with 406')

    @tags(type='negative')
    def test_putting_secret_that_doesnt_exist(self):
        """ Covers case of putting secret information to a non-existent
        secret. Should return 404.
        """
        resp = self.client.add_secret_payload(
            secret_id='not_a_uuid',
            payload_content_type=self.config.payload_content_type,
            payload='testing putting to non-existent secret')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    @unittest.skip("Blueprint barbican-enforce-content-type")
    @tags(type='negative')
    def test_putting_w_invalid_content_type(self):
        """ Covers case of putting secret information with an
        invalid content type. Should return 415.
        - Reported in Barbican Launchpad Bug #1208601
        - Updated in Barbican blueprint barbican-enforce-content-type
        """
        resp = self.behaviors.create_secret()
        put_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type='crypto/boom',
            payload='testing putting with invalid mime type')
        self.assertEqual(put_resp.status_code, 415,
                         'Should have failed with 415')

    @tags(type='negative')
    def test_putting_secret_w_data_already(self):
        """ Covers case of putting secret information to a secret that already
        has encrypted data associated with it. Should return 409.
        """
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        put_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type=self.config.payload_content_type,
            payload='testing putting to a secret that already has data')
        self.assertEqual(put_resp.status_code, 409,
                         'Should have failed with 409')

    @tags(type='negative')
    def test_putting_w_empty_data(self):
        """
        Covers case of putting empty String to a secret. Should return 400.
        """
        resp = self.behaviors.create_secret()
        put_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type=self.config.payload_content_type,
            payload='')
        self.assertEqual(put_resp.status_code, 400,
                         'Should have failed with 400')

    @skip_open_issue('launchpad', '1315498')
    @skip_open_issue('launchpad', '1321502')
    @tags(type='negative')
    def test_putting_w_oversized_binary_data_no_utf8(self):
        """
        Covers case of putting an oversized string with binary data that
        doesn't contain UTF-8 code points.  This tests bug 1315498.
        """
        resp = self.behaviors.create_secret()

        data = bytearray().zfill(
            self.cloudkeep.max_allowed_secret_in_bytes + 1)

        # put a value in the middle of the data that does not have a UTF-8
        # code point.  Using // to be python3-friendly.
        data[self.cloudkeep.max_allowed_secret_in_bytes // 2] = b'\xb0'

        put_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type='application/octet-stream',
            payload_content_encoding='base64',
            payload=str(data))
        self.assertEqual(put_resp.status_code, 413,
                         'Returned unexpected response code')

    @skip_open_issue('launchpad', '1315498')
    @skip_open_issue('launchpad', '1354567')
    @tags(type='positive')
    def test_putting_w_valid_binary_data_no_utf8(self):
        """
        Covers case of putting a string with binary data that doesn't
        contain UTF-8 code points.  This tests bug 1315498.
        """
        resp = self.behaviors.create_secret()

        # put a value in the data that does not have a UTF-8 code point.
        data = b'\xb0'

        put_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type='application/octet-stream',
            payload_content_encoding='base64',
            payload=str(data))
        self.assertEqual(put_resp.status_code, 204,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_putting_w_null_data(self):
        """Covers case of putting null String to a secret.
        Should return 400.
        """
        resp = self.behaviors.create_secret()
        put_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type=self.config.payload_content_type,
            payload=None)
        self.assertEqual(put_resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_putting_w_oversized_data(self):
        """ Covers case of putting secret data that is larger than the maximum
        secret size allowed by Barbican. Beyond that it should return 413.
        """
        data = bytearray().zfill(
            self.cloudkeep.max_allowed_secret_in_bytes + 1)
        resp = self.behaviors.create_secret()
        put_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type=self.config.payload_content_type,
            payload=str(data))
        self.assertEqual(put_resp.status_code, 413,
                         'Should have failed with 413')

    @tags(type='negative')
    def test_deleting_secret_that_doesnt_exist(self):
        """
        Covers case of deleting a non-existent secret. Should return 404.
        """
        resp = self.behaviors.delete_secret(secret_id='not_a_uuid')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    @tags(type='negative')
    def test_creating_secret_w_invalid_expiration(self):
        """
        Covers creating secret with expiration that has already passed.
        Should return 400.
        """
        resp = self.behaviors.create_secret_overriding_cfg(
            expiration='2000-01-10T14:58:52.546795')
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='positive')
    def test_checking_content_types_when_data(self):
        """ Covers checking that content types attribute is shown when secret
        has encrypted data associated with it.
        """
        resps = self.behaviors.create_and_check_secret(
            payload_content_type=self.config.payload_content_type)
        secret = resps.get_resp.entity
        content_types = secret.content_types
        self.assertIsNotNone(content_types,
                             'Should have had content types attribute')
        self.assertIn('default', content_types)
        self.assertEqual(content_types['default'],
                         self.config.payload_content_type,
                         'Default content type not correct')

    @tags(type='negative')
    def test_checking_no_content_types_when_no_data(self):
        """ Covers checking that the secret create fails when a content type
        is passed in without any payload data.
        """
        create_resp = self.behaviors.create_secret(
            payload_content_type=self.config.payload_content_type)
        self.assertEqual(create_resp.status_code, 400,
                         'Should have failed with 400 since no payload')

    @tags(type='negative')
    def test_creating_secret_w_only_content_type_and_encoding(self):
        """ Covers creating secret with only content type and encoding, with
        no payload.  Should return 400.
        """
        resp = self.behaviors.create_secret(
            payload_content_type=self.config.payload_content_type,
            payload_content_encoding=self.config.payload_content_encoding)
        self.assertEqual(resp.status_code, 400,
                         'Should fail with 400 since no payload specified')

    @tags(type='positive')
    def test_creating_secret_w_aes_algorithm(self):
        """Covers case of creating a secret with an aes algorithm."""
        resp = self.behaviors.create_secret_overriding_cfg(algorithm='aes')
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_cbc_mode(self):
        """Covers case of creating a secret with a cbc cypher type."""
        resp = self.behaviors.create_secret_overriding_cfg(mode='cbc')
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_secret_hostname_response(self):
        """Covers case of checking that hostname of secret_ref is the same
        as the configured hostname.
        - Reported in Barbican GitHub Issue #182
        """
        create_resp = self.behaviors.create_secret_from_config()
        self.assertEqual(create_resp.status_code, 201,
                         'Returned unexpected response code')

        # Get secret using returned secret_ref
        ref_get_resp = self.client.get_secret(ref=create_resp.ref)
        self.assertEqual(ref_get_resp.status_code, 200,
                         'Returned unexpected response code')

        # Get secret using secret id and configured base url
        config_get_resp = self.client.get_secret(
            secret_id=create_resp.id)
        self.assertEqual(config_get_resp.status_code, 200,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_creating_secret_w_text_plain_mime_type_no_payload(self):
        """Covers case of attempting to create a secret with text/plain as
        mime type, with no payload.  Should result in 400"""
        resp = self.behaviors.create_secret(payload_content_type='text/plain')
        self.assertEqual(resp.status_code, 400,
                         'Should fail with 400 since no payload specified')

    @tags(type='positive')
    def test_creating_secret_w_text_plain_mime_type(self):
        """Covers case of attempting to create a secret with text/plain as
        mime type"""
        resp = self.behaviors.create_secret(payload="an interesting payload",
                                            payload_content_type='text/plain')
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_app_octet_mime_type_and_base64(self):
        """Covers case of creating a secret with application/octet-stream
        content type and base64 encoding."""
        resp = self.behaviors.create_secret(
            payload_content_type='application/octet-stream',
            payload_content_encoding='base64',
            payload=self.config.payload)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    def _calculate_available_size(self):
        """Calculate the maximum size for an item within a secret when
        testing maximum request and secret sizes.  We do this by creating a
        JSON string matching the request and then finding out how much space
        is left for inserting item values."""

        my_dict = {'name': '', 'mode': '', 'algorithm': '',
                   'payload': self.config.payload,
                   'payload_content_type': self.config.payload_content_type,
                   'payload_content_encoding':
                   self.config.payload_content_encoding}

        json_str = json.dumps(my_dict)

        return self.cloudkeep.max_allowed_request_size_in_bytes - len(json_str)

    @skip_open_issue('launchpad', '1330238')
    @tags(type='negative')
    def test_creating_secret_w_large_string_values_oversize_by_one(self):
        """Covers case of creating secret with large string values such
        that the total request is 1 byte larger than the maximum allowed.
        We will use large strings to populate the following fields:

             1. name
             2. algorithm
             3. mode"""

        available_size = self._calculate_available_size()
        available_size_per_item = available_size // 3
        rest_of_available_size = available_size % 3

        large_string = str(bytearray().zfill(available_size_per_item))

        # this string will make the entire payload 1 byte larger than the max
        a_larger_string = str(bytearray().zfill(
            available_size_per_item + rest_of_available_size + 1))

        resp = self.behaviors.create_secret(
            payload_content_type=self.config.payload_content_type,
            payload=self.config.payload,
            payload_content_encoding=self.config.payload_content_encoding,
            name=a_larger_string,
            algorithm=large_string,
            mode=large_string)
        self.assertEqual(resp.status_code, 413,
                         'Returned unexpected response code')

    @tags(type='positive')
    @skip_open_issue('launchpad', '1335327')
    def test_creating_secret_w_large_string_values(self):
        """Covers case of creating secret with large String values such
        that the total request size is the maximum size allowed.
        We will use the large_string to populate the following fields:

             1. name
             2. algorithm
             3. mode

        We will make these fields sufficiently large such that we come up
        against, but not over, the maximum overall request size."""

        available_size = self._calculate_available_size()
        available_size_per_item = available_size // 3
        rest_of_available_size = available_size % 3

        large_string = str(bytearray().zfill(available_size_per_item))

        # use this string for one field to ensure that the total payload
        # is the maximum length
        a_larger_string = str(bytearray().zfill(
            available_size_per_item + rest_of_available_size))

        resp = self.behaviors.create_secret(
            payload_content_type=self.config.payload_content_type,
            payload=self.config.payload,
            payload_content_encoding=self.config.payload_content_encoding,
            name=large_string,
            algorithm=large_string,
            mode=a_larger_string)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_max_secret_size(self):
        """Covers case of creating secret whose payload is the maximum size
        allowed by Barbican."""
        large_string = str(bytearray().zfill(
            self.cloudkeep.max_allowed_secret_in_bytes))
        resp = self.behaviors.create_secret(
            payload_content_type=self.config.payload_content_type,
            payload_content_encoding=self.config.payload_content_encoding,
            payload=large_string)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_creating_secret_w_int_as_name(self):
        """Covers case of creating a secret with an integer as the name.
        Should return 400."""
        resp = self.behaviors.create_secret_overriding_cfg(name=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_int_as_algorithm(self):
        """Covers case of creating a secret with an integer as the algorithm.
        Should return 400."""
        resp = self.behaviors.create_secret_overriding_cfg(algorithm=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_invalid_algorithm(self):
        """Covers case of creating a secret with an invalid algorithm."""
        resp = self.behaviors.create_secret_overriding_cfg(
            algorithm='invalid_algorithm')
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_creating_secret_w_int_as_mode(self):
        """Covers case of creating a secret with an integer as the cypher type.
        Should return 400.
        """
        resp = self.behaviors.create_secret_overriding_cfg(mode=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='positive')
    def test_creating_secret_w_charset(self):
        """Covers creating a secret with text/plain; charset=utf-8 as content
        type."""
        resp = self.behaviors.create_secret(
            payload_content_type='text/plain; charset=utf-8',
            payload=self.config.payload)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    def test_get_secret_payload_with_a_octet_stream(self):
        content_type = 'application/octet-stream'
        b64_payload = 'abcdef'
        encoding = 'base64'

        create_resp = self.behaviors.create_secret_overriding_cfg(
            payload_content_type=content_type,
            payload_content_encoding=encoding,
            payload=base64.b64encode(b64_payload))

        self.assertEqual(create_resp.status_code, 201)

        get_resp = self.client.get_secret(create_resp.id,
                                          payload_content_type=content_type,
                                          payload_content_encoding=encoding)
        self.assertEqual(get_resp.content, b64_payload)

    @skip_open_issue('launchpad', '1321439')
    def test_message_from_create_secret_with_bad_content_type(self):
        """ will create a secret with an "invalid" content type
        (plain-text, rather than text/plain).  This will result in
        an error, and we need to ensure that the error msg is
        reasonable.
        """
        resp = self.behaviors.create_secret_overriding_cfg(
            payload_content_type='plain-text; charset=utf-8')

        create_resp = resp.create_resp

        # first, ensure that the return code is 400
        self.assertEqual(create_resp.status_code, 400)
        pattern = (
            r".*\"description\": \"Provided object does not match schema "
            "'Secret': (.*?) is not one of (.*?)\".*")
        regex_opts = re.DOTALL | re.MULTILINE
        result = re.match(pattern, create_resp.content, regex_opts)

        # now see that the regexp matched (ie result is not None)
        self.assertIsNotNone(result, 'Error message was not as expected')

    @skip_open_issue('launchpad', '1254169')
    def test_create_secret_with_only_content_type(self):
        resp = self.behaviors.create_secret(payload_content_type='text/plain')
        self.assertEqual(resp.create_resp.status_code, 400)

    @tags(type='negative')
    def test_create_secret_with_no_json(self):
        """Covers case of a POST request with no JSON data."""
        resp = self.behaviors.create_secret_with_no_json()
        self.assertEqual(resp.create_resp.status_code, 400)

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
        create_resp = self.behaviors.create_secret_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(create_resp.status_code, 201)

        # now get the secret - will be still valid
        resp = self.client.get_secret(create_resp.id)
        self.assertEqual(resp.status_code, 200)

        # now wait 3 minutes
        sleep(3 * 60)

        # now get the secret - should be invalid (expired)
        resp = self.client.get_secret(create_resp.id)
        self.assertEqual(resp.status_code, 404)

    @tags(type='positive')
    @skip_open_issue('launchpad', '1350988')
    def test_update_secret_with_high_range_unicode_character(self):
        """Ensure a two step secret creation succeeds with Content-Type
        application/octet-stream and a high range unicode character.
        Launchpad bug #1315498
        """
        resp = self.behaviors.create_secret(name='beer')
        beer_char = u'\U0001F37A'
        payload_resp = self.client.add_secret_payload(
            resp.id, 'application/octet-stream', beer_char.encode('utf-8'))

        self.assertEqual(payload_resp.status_code, 204)


class SecretsPagingAPI(SecretsPagingFixture):

    @skip_open_issue('launchpad', '1321497')
    @tags(type='positive')
    def test_find_a_single_secret_via_paging(self):
        """ Covers case where when you attempt to retrieve a list of secrets,
        if the limit is set higher than 8, the next attribute in the response
        is not available.
        - Reported in Barbican GitHub Issue #81
        """
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        secret = self.behaviors.find_secret(resp.id)
        self.assertIsNotNone(secret, 'Couldn\'t find created secret')

    @tags(type='positive')
    def test_paging_limit_and_offset(self):
        """Covers testing paging limit and offset attributes
        when getting secrets.
        """
        # First set of secrets
        resp = self.client.get_secrets(limit=10, offset=0)
        sec_group1 = self._check_list_of_secrets(resp=resp, limit=10)

        # Second set of secrets
        resp = self.client.get_secrets(limit=10, offset=10)
        sec_group2 = self._check_list_of_secrets(resp=resp, limit=10)

        self._check_for_duplicates(group1=sec_group1.secrets,
                                   group2=sec_group2.secrets)

    @tags(type='positive')
    def test_secret_paging_next_option(self):
        """Covers getting a list of secrets and using the next
        reference.
        """
        # First set of secrets
        resp = self.client.get_secrets(limit=15, offset=115)
        sec_group1 = self._check_list_of_secrets(resp=resp, limit=15)
        next_ref = sec_group1.next
        self.assertIsNotNone(next_ref)

        # Next set of secrets
        resp = self.client.get_secrets(ref=next_ref)
        sec_group2 = self._check_list_of_secrets(resp=resp, limit=15)

        self._check_for_duplicates(group1=sec_group1.secrets,
                                   group2=sec_group2.secrets)

    @tags(type='positive')
    def test_secret_paging_previous_option(self):
        """Covers getting a list of secrets and using the previous
        reference.
        """
        # First set of secrets
        resp = self.client.get_secrets(limit=15, offset=115)
        sec_group1 = self._check_list_of_secrets(resp=resp, limit=15)
        previous_ref = sec_group1.previous
        self.assertIsNotNone(previous_ref)

        # Previous set of secrets
        resp = self.client.get_secrets(ref=previous_ref)
        sec_group2 = self._check_list_of_secrets(resp=resp, limit=15)

        self._check_for_duplicates(group1=sec_group1.secrets,
                                   group2=sec_group2.secrets)

    @tags(type='positive')
    def test_secret_paging_max_limit(self):
        """Covers case of listing secrets with a limit more than the current
        maximum of 100.
        """
        resp = self.client.get_secrets(limit=101, offset=0)
        self._check_list_of_secrets(resp=resp, limit=100)

    @tags(type='positive')
    def test_secret_paging_limit(self):
        """Covers listing secrets with limit attribute from limits
        of 2 to 25.
        """
        for limit in range(2, 25):
            resp = self.client.get_secrets(limit=limit, offset=0)
            self._check_list_of_secrets(resp=resp, limit=limit)

    @tags(type='positive')
    def test_secret_paging_offset(self):
        """Covers listing secrets with offset attribute from offsets
        of 2 to 25.
        """
        # Covers offsets between 1 and 25
        for offset in range(1, 24):
            resp = self.client.get_secrets(limit=2, offset=offset)
            sec_group1 = self._check_list_of_secrets(resp=resp, limit=2)
            previous_ref1 = sec_group1.previous
            self.assertIsNotNone(previous_ref1)
            next_ref1 = sec_group1.next
            self.assertIsNotNone(next_ref1)

            resp = self.client.get_secrets(limit=2, offset=offset + 2)
            sec_group2 = self._check_list_of_secrets(resp=resp, limit=2)
            previous_ref2 = sec_group2.previous
            self.assertIsNotNone(previous_ref2)
            next_ref2 = sec_group2.next
            self.assertIsNotNone(next_ref2)

            self._check_for_duplicates(group1=sec_group1.secrets,
                                       group2=sec_group2.secrets)

    @tags(type='positive')
    def test_secret_paging_w_invalid_parameters(self):
        """ Covers listing secrets with invalid limit and offset parameters.
        - Reported in Barbican GitHub Issue #171
        """
        self.behaviors.create_secret_from_config(use_expiration=False)
        resp = self.client.get_secrets(limit='not-an-int', offset='not-an-int')
        self.assertEqual(resp.status_code, 200,
                         'Returned unexpected response code')
