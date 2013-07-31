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
from datetime import datetime, timedelta
from uuid import uuid4
from sys import maxint
import unittest2

from cloudroast.cloudkeep.barbican.fixtures import SecretsFixture, \
    SecretsPagingFixture
from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools import randomstring


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
    def test_secret_with_plain_text_deletion(self):
        """ Covers case where the system fails to delete a secret if it
        contains a set "plain_text" field.
        - Reported in Barbican GitHub Issue #77
        """
        resp = self.behaviors.create_secret_from_config(use_expiration=False,
                                                        use_plain_text=True)
        self.assertEqual(resp.status_code, 201)

        del_resp = self.behaviors.delete_secret(resp.id)
        self.assertEqual(del_resp.status_code, 200)

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
    def test_creating_secret_w_bit_length(self):
        """ Covers creating secret with a bit length. """
        resps = self.behaviors.create_and_check_secret(bit_length=512)
        secret = resps.get_resp.entity
        self.assertEqual(resps.get_resp.status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 512)

    @tags(type='negative')
    def test_creating_w_null_entries(self):
        """ Covers case when you push a secret full of nulls. This should
        return a 400.
        - Reported in Barbican GitHub Issue #90
        """
        resp = self.behaviors.create_secret()
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_w_empty_entries(self):
        """ Covers case of creating a secret with empty Strings for all
        entries. Should return a 400.
        """
        resp = self.behaviors.create_secret(name='',
                                            expiration='',
                                            algorithm='',
                                            cypher_type='',
                                            plain_text='',
                                            mime_type='')
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='positive')
    def test_creating_w_empty_name(self):
        """ When a test is created with an empty or null name attribute, the
         system should return the secret's UUID on a get
         - Reported in Barbican GitHub Issue #89
        """
        c_resp = self.behaviors.create_secret(name='',
                                              mime_type=self.config.mime_type)

        get_resp = self.client.get_secret(secret_id=c_resp.id)
        self.assertEqual(get_resp.entity.name, c_resp.id,
                         'Name doesn\'t match UUID of secret')

    @tags(type='positive')
    def test_creating_w_null_name(self):
        """ When a test is created with an empty or null name attribute, the
         system should return the secret's UUID on a get
         - Reported in Barbican GitHub Issue #89
        """
        c_resp = self.behaviors.create_secret(name=None,
                                              mime_type=self.config.mime_type)

        get_resp = self.client.get_secret(secret_id=c_resp.id)
        self.assertEqual(get_resp.entity.name, c_resp.id,
                         'Name doesn\'t match UUID of secret')

    @tags(type='negative')
    def test_creating_w_empty_mime_type(self):
        """Covers creating a secret with an empty String as the mime type.
        Should return a 400."""
        resp = self.behaviors.create_secret(mime_type='')
        self.assertEqual(resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_creating_w_null_mime_type(self):
        """Covers creating a secret without a mime type.
        Should return a 400."""
        resp = self.behaviors.create_secret(
            name=self.config.name,
            plain_text=self.config.plain_text,
            algorithm=self.config.algorithm,
            cypher_type=self.config.cypher_type,
            bit_length=self.config.bit_length,
            mime_type=None
        )
        self.assertEqual(resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_creating_w_empty_secret(self):
        """Covers creating a secret with an empty String as the plain
        text value."""
        resp = self.behaviors.create_secret(mime_type=self.config.mime_type,
                                            plain_text='')
        self.assertEqual(resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_creating_w_oversized_secret(self):
        """ Covers creating a secret with a secret that is larger than
        the limit. Current size limit is 10k bytes. Beyond that,
        it should return 413.
        """
        data = bytearray().zfill(10001)

        resps = self.behaviors.create_and_check_secret(plain_text=str(data))
        self.assertEqual(resps.create_resp.status_code, 413,
                         'Should have failed with 413')

    @tags(type='negative')
    def test_creating_w_invalid_mime_type(self):
        """Covers creating a secret with an invalid mime type."""
        resps = self.behaviors.create_and_check_secret(mime_type='crypto/boom')
        self.assertEqual(resps.create_resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_getting_secret_that_doesnt_exist(self):
        """Covers getting a nonexistent secret."""
        resp = self.client.get_secret('not_a_uuid')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    @tags(type='negative')
    def test_getting_secret_data_w_invalid_mime_type(self):
        """Covers getting a secret with an invalid mime type."""
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        resp = self.client.get_secret(resp.id, mime_type='i/m')
        self.assertEqual(resp.status_code, 406, 'Should have failed with 406')

    @tags(type='negative')
    def test_creating_w_plain_text_as_array(self):
        """Covers creating a secret with the plain text value as an array."""
        resps = self.behaviors.create_and_check_secret(plain_text=['boom'])
        self.assertEqual(resps.create_resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_putting_secret_that_doesnt_exist(self):
        """ Covers case of putting secret information to a non-existent
        secret. Should return 404.
        """
        resp = self.client.add_secret_plain_text(
            secret_id='not_a_uuid',
            mime_type=self.config.mime_type,
            plain_text='testing putting to non-existent secret')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    @tags(type='negative')
    def test_putting_w_invalid_mime_type(self):
        """ Covers case of putting secret information with an
        invalid mime-type. Should return 400.
        """
        resp = self.behaviors.create_secret(mime_type=self.config.mime_type)
        put_resp = self.client.add_secret_plain_text(
            secret_id=resp.id,
            mime_type='crypto/boom',
            plain_text='testing putting with invalid mime type')
        self.assertEqual(put_resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_putting_secret_w_data_already(self):
        """ Covers case of putting secret information to a secret that already
        has encrypted data associated with it. Should return 409.
        """
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        put_resp = self.client.add_secret_plain_text(
            secret_id=resp.id,
            mime_type=self.config.mime_type,
            plain_text='testing putting to a secret that already has data')
        self.assertEqual(put_resp.status_code, 409,
                         'Should have failed with 409')

    @tags(type='negative')
    def test_putting_w_empty_data(self):
        """
        Covers case of putting empty String to a secret. Should return 400.
        """
        resp = self.behaviors.create_secret(mime_type=self.config.mime_type)
        put_resp = self.client.add_secret_plain_text(
            secret_id=resp.id,
            mime_type=self.config.mime_type,
            plain_text='')
        self.assertEqual(put_resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_putting_w_null_data(self):
        """Covers case of putting null String to a secret.
        Should return 400.
        """
        resp = self.behaviors.create_secret(mime_type=self.config.mime_type)
        put_resp = self.client.add_secret_plain_text(
            secret_id=resp.id,
            mime_type=self.config.mime_type,
            plain_text=None)
        self.assertEqual(put_resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='negative')
    def test_putting_w_oversized_data(self):
        """ Covers case of putting secret data that is beyond size limit.
        Current size limit is 10k bytes. Beyond that it should return 413.
        """
        data = bytearray().zfill(10001)
        resp = self.behaviors.create_secret(mime_type=self.config.mime_type)
        put_resp = self.client.add_secret_plain_text(
            secret_id=resp.id,
            mime_type=self.config.mime_type,
            plain_text=str(data))
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
        resps = self.behaviors.create_and_check_secret()
        secret = resps.get_resp.entity
        self.assertIsNotNone(secret.content_types,
                             'Should not have had content types')

    @tags(type='positive')
    def test_checking_no_content_types_when_no_data(self):
        """ Covers checking that the content types attribute is not shown if
        the secret does not have encrypted data associated with it.
        """
        create_resp = self.behaviors.create_secret(
            mime_type=self.config.mime_type)
        secret_id = create_resp.id
        resp = self.client.get_secret(secret_id=secret_id)
        secret = resp.entity
        self.assertIsNone(secret.content_types,
                          'Should have had content types')

    @tags(type='negative')
    def test_creating_secret_w_invalid_bit_length(self):
        """ Cover case of creating a secret with a bit length that is not
        an integer. Should return 400.
        """
        resp = self.behaviors.create_secret_overriding_cfg(
            bit_length='not-an-int')
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_negative_bit_length(self):
        """ Covers case of creating a secret with a bit length
        that is negative. Should return 400.
        """
        resp = self.behaviors.create_secret_overriding_cfg(
            bit_length=-1)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='positive')
    def test_creating_secret_w_only_mime_type(self):
        """ Covers creating secret with only required fields. In this case,
        only mime type is required.
        """
        resp = self.behaviors.create_secret(mime_type=self.config.mime_type)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_alphanumeric_name(self):
        """Covers case of creating secret with an alphanumeric name."""
        name = randomstring.get_random_string(prefix='1a2b')
        resps = self.behaviors.create_and_check_secret(name=name)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Returned unexpected response code')
        secret = resps.get_resp.entity
        self.assertEqual(secret.name, name, 'Secret name is not correct')

    @tags(type='positive')
    def test_creating_secret_w_punctuation_in_name(self):
        """Covers case of creating a secret with miscellaneous punctuation and
        symbols in the name.
        """
        name = '~!@#$%^&*()_+`-={}[]|:;<>,.?"'
        resps = self.behaviors.create_and_check_secret(name=name)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(secret.name, name, 'Secret name is not correct')

    @tags(type='positive')
    def test_creating_secret_w_uuid_as_name(self):
        """Covers case of creating a secret with a random uuid as the name."""
        uuid = str(uuid4())
        resps = self.behaviors.create_and_check_secret(name=uuid)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(secret.name, uuid, 'Secret name is not correct')

    @tags(type='positive')
    def test_create_secret_w_name_of_len_255(self):
        """Covers case of creating a secret with a 255 character name."""
        name = randomstring.get_random_string(size=255)
        resps = self.behaviors.create_and_check_secret(name=name)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(secret.name, name, 'Secret name is not correct')

    @tags(type='positive')
    def test_creating_secret_w_128_bit_length(self):
        """Covers case of creating a secret with a 128 bit length."""
        resps = self.behaviors.create_and_check_secret(bit_length=128)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(resps.get_resp.status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 128)

    @tags(type='positive')
    def test_creating_secret_w_192_bit_length(self):
        """Covers case of creating a secret with a 192 bit length."""
        resps = self.behaviors.create_and_check_secret(bit_length=192)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(resps.get_resp.status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 192)

    @tags(type='positive')
    def test_creating_secret_w_256_bit_length(self):
        """Covers case of creating a secret with a 256 bit length."""
        resps = self.behaviors.create_and_check_secret(bit_length=256)
        self.assertEqual(resps.create_resp.status_code, 201,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity
        self.assertEqual(resps.get_resp.status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 256)

    @tags(type='positive')
    def test_creating_secret_w_aes_algorithm(self):
        """Covers case of creating a secret with an aes algorithm."""
        resp = self.behaviors.create_secret_overriding_cfg(algorithm='aes')
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_cbc_cypher_type(self):
        """Covers case of creating a secret with a cbc cypher type."""
        resp = self.behaviors.create_secret_overriding_cfg(cypher_type='cbc')
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

    @tags(type='positive')
    def test_creating_secret_w_text_plain_mime_type(self):
        """Covers case of creating a secret with text/plain as mime type."""
        resp = self.behaviors.create_secret_overriding_cfg(
            mime_type='text/plain')
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_app_octet_mime_type(self):
        """Covers case of creating a secret with application/octet-stream
        as mime type."""
        resp = self.behaviors.create_secret(
            mime_type='application/octet-stream')
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_empty_checking_name(self):
        """ When an secret is created with an empty name attribute, the
        system should return the secret's UUID on a get. Extends coverage of
        test_creating_w_empty_name.
        """
        resp = self.behaviors.create_secret(
            mime_type=self.config.mime_type,
            name="",
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)

        get_resp = self.client.get_secret(resp.id)
        secret = get_resp.entity
        self.assertEqual(secret.name, secret.get_id(),
                         'Name did not match secret\'s UUID')

    @tags(type='positive')
    def test_creating_secret_wout_name_checking_name(self):
        """ When a secret is created with a null name attribute, the
        system should return the secret's UUID on a get. Extends coverage of
        test_creating_w_null_name.
        """
        resp = self.behaviors.create_secret(
            mime_type=self.config.mime_type,
            name=None,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)

        get_resp = self.client.get_secret(resp.id)
        secret = get_resp.entity
        self.assertEqual(secret.name, secret.get_id(),
                         'Name did not match secret\'s UUID')

    @tags(type='positive')
    def test_creating_secret_w_large_string_values(self):
        """Covers case of creating secret with large String values."""
        large_string = str(bytearray().zfill(10001))
        resp = self.behaviors.create_secret(
            mime_type=self.config.mime_type,
            name=large_string,
            algorithm=large_string,
            cypher_type=large_string)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_max_secret_size(self):
        """Covers case of creating secret with the maximum value for
        an encrypted secret. Current limit is 10k bytes."""
        large_string = str(bytearray().zfill(10000))
        resp = self.behaviors.create_secret(
            mime_type=self.config.mime_type,
            plain_text=large_string)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_creating_secret_w_large_bit_length(self):
        """Covers case of creating secret with a large integer as
        the bit length."""
        resp = self.behaviors.create_secret(
            mime_type=self.config.mime_type,
            bit_length=maxint)
        self.assertEqual(resp.status_code, 201,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_creating_secret_w_large_string_as_bit_length(self):
        """Covers case of creating secret with a large String as
        the bit length. Should return 400."""
        large_string = str(bytearray().zfill(10001))
        resp = self.behaviors.create_secret(
            mime_type=self.config.mime_type,
            bit_length=large_string)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_large_string_as_mime_type(self):
        """Covers case of creating secret with a large String as
        the bit length. Should return 400."""
        large_string = str(bytearray().zfill(10001))
        resp = self.behaviors.create_secret(mime_type=large_string)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_int_as_name(self):
        """Covers case of creating a secret with an integer as the name.
        Should return 400."""
        resp = self.behaviors.create_secret_overriding_cfg(name=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_int_as_mime_type(self):
        """Covers case of creating a secret with an integer as the mime type.
        Should return 400."""
        resp = self.behaviors.create_secret_overriding_cfg(mime_type=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_int_as_algorithm(self):
        """Covers case of creating a secret with an integer as the algorithm.
        Should return 400."""
        resp = self.behaviors.create_secret_overriding_cfg(algorithm=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_int_as_cypher_type(self):
        """Covers case of creating a secret with an integer as the cypher type.
        Should return 400."""
        resp = self.behaviors.create_secret_overriding_cfg(cypher_type=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_secret_w_app_octet_mime_type_and_plain_text(self):
        """Covers case of creating a secret with application/octet-stream
        as mime type and a plain_text value provided. Should return 400.
        - Reported in Barbican Launchpad Bug #1200659"""
        resp = self.behaviors.create_secret(
            mime_type='application/octet-stream',
            plain_text=self.config.plain_text)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')


class SecretsPagingAPI(SecretsPagingFixture):

    def check_list_of_secrets(self, resp, limit):
        """Checks that the response from getting list of secrets
        returns a 200 status code and the correct number of secrets.
        Also returns the list of secrets from the response.
        """
        self.assertEqual(resp.status_code, 200,
                         'Returned unexpected response code')
        sec_group = resp.entity
        self.assertEqual(len(sec_group.secrets), limit,
                         'Returned wrong number of secrets')
        return resp.entity

    def check_for_duplicates(self, sec_group1, sec_group2):
        """Checks for duplicated secrets between two groups of secrets."""
        duplicates = [secret for secret in sec_group1.secrets
                      if secret in sec_group2.secrets]
        self.assertEqual(len(duplicates), 0,
                         'Lists of secrets did not return unique secrets')

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
        sec_group1 = self.check_list_of_secrets(resp=resp, limit=10)

        # Second set of secrets
        resp = self.client.get_secrets(limit=10, offset=10)
        sec_group2 = self.check_list_of_secrets(resp=resp, limit=10)

        self.check_for_duplicates(sec_group1=sec_group1, sec_group2=sec_group2)

    @tags(type='positive')
    def test_secret_paging_next_option(self):
        """Covers getting a list of secrets and using the next
        reference.
        """
        # First set of secrets
        resp = self.client.get_secrets(limit=15, offset=115)
        sec_group1 = self.check_list_of_secrets(resp=resp, limit=15)
        next_ref = sec_group1.next
        self.assertIsNotNone(next_ref)

        #Next set of secrets
        resp = self.client.get_secrets(ref=next_ref)
        sec_group2 = self.check_list_of_secrets(resp=resp, limit=15)

        self.check_for_duplicates(sec_group1=sec_group1, sec_group2=sec_group2)

    @tags(type='positive')
    def test_secret_paging_previous_option(self):
        """Covers getting a list of secrets and using the previous
        reference.
        """
        # First set of secrets
        resp = self.client.get_secrets(limit=15, offset=115)
        sec_group1 = self.check_list_of_secrets(resp=resp, limit=15)
        previous_ref = sec_group1.previous
        self.assertIsNotNone(previous_ref)

        #Previous set of secrets
        resp = self.client.get_secrets(ref=previous_ref)
        sec_group2 = self.check_list_of_secrets(resp=resp, limit=15)

        self.check_for_duplicates(sec_group1=sec_group1, sec_group2=sec_group2)

    @tags(type='positive')
    def test_secret_paging_max_limit(self):
        """Covers case of listing secrets with a limit more than the current
        maximum of 100.
        """
        resp = self.client.get_secrets(limit=101, offset=0)
        self.check_list_of_secrets(resp=resp, limit=100)

    @tags(type='positive')
    def test_secret_paging_limit(self):
        """Covers listing secrets with limit attribute from limits
        of 2 to 25.
        """
        for limit in range(2, 25):
            resp = self.client.get_secrets(limit=limit, offset=0)
            self.check_list_of_secrets(resp=resp, limit=limit)

    @tags(type='positive')
    def test_secret_paging_offset(self):
        """Covers listing secrets with offset attribute from offsets
        of 2 to 25.
        """
        # Covers offsets between 1 and 25
        for offset in range(1, 24):
            resp = self.client.get_secrets(limit=2, offset=offset)
            sec_group1 = self.check_list_of_secrets(resp=resp, limit=2)
            previous_ref1 = sec_group1.previous
            self.assertIsNotNone(previous_ref1)
            next_ref1 = sec_group1.next
            self.assertIsNotNone(next_ref1)

            resp = self.client.get_secrets(limit=2, offset=offset + 2)
            sec_group2 = self.check_list_of_secrets(resp=resp, limit=2)
            previous_ref2 = sec_group2.previous
            self.assertIsNotNone(previous_ref2)
            next_ref2 = sec_group2.next
            self.assertIsNotNone(next_ref2)

            self.check_for_duplicates(sec_group1=sec_group1,
                                      sec_group2=sec_group2)

    @tags(type='positive')
    def test_secret_paging_w_invalid_parameters(self):
        """ Covers listing secrets with invalid limit and offset parameters.
        - Reported in Barbican GitHub Issue #171
        """
        self.behaviors.create_secret_from_config(use_expiration=False)
        resp = self.client.get_secrets(limit='not-an-int', offset='not-an-int')
        self.assertEqual(resp.status_code, 200,
                         'Returned unexpected response code')
