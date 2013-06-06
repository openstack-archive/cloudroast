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
from test_repo.cloudkeep.barbican.fixtures import SecretsFixture


class SecretsAPI(SecretsFixture):

    def check_expiration_iso8601_timezone(self, timezone, offset):
        one_day_ahead = (datetime.today() + timedelta(days=1))
        timestamp = '{time}{timezone}'.format(
            time=one_day_ahead,
            timezone=timezone)

        resp = self.behaviors.create_secret_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp['status_code'], 201)

        secret = self.client.get_secret(resp['secret_id']).entity
        exp = datetime.strptime(secret.expiration, '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(exp, one_day_ahead + timedelta(hours=offset),
                         'Response didn\'t return the expected time')

    def check_invalid_expiration_timezone(self, timezone):
        timestamp = '{time}{timezone}'.format(
            time=(datetime.today() + timedelta(days=1)),
            timezone=timezone)

        resp = self.behaviors.create_secret_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp['status_code'], 400)

    def test_secret_with_plain_text_deletion(self):
        """ Covers case where the system fails to delete a secret if it
        contains a set "plain_text" field.
        - Reported in Barbican GitHub Issue #77
        """
        resp = self.behaviors.create_secret_from_config(use_expiration=False,
                                                        use_plain_text=True)
        self.assertEqual(resp['status_code'], 201)

        del_resp = self.behaviors.delete_secret(resp['secret_id'])
        self.assertEqual(del_resp.status_code, 200)

    def test_create_secret_with_long_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #131
        """
        self.check_expiration_iso8601_timezone('-05:00', 5)
        self.check_expiration_iso8601_timezone('+05:00', -5)

    def test_create_secret_with_short_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #135
        """
        self.check_expiration_iso8601_timezone('-01', 1)
        self.check_expiration_iso8601_timezone('+01', -1)

    def test_create_secret_with_bad_expiration_timezone(self):
        """ Covers case of a malformed timezone being added to the expiration.
        - Reported in Barbican GitHub Issue #134
        """
        self.check_invalid_expiration_timezone('-5:00')

    def test_find_a_single_secret_via_paging(self):
        """ Covers case where when you attempt to retrieve a list of secrets,
        if the limit is set higher than 8, the next attribute in the response
        is not available.
        - Reported in Barbican GitHub Issue #81
        """
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        for count in range(1, 11):
            self.behaviors.create_secret_from_config(use_expiration=False)
        secret = self.behaviors.find_secret(resp['secret_id'])
        self.assertIsNotNone(secret, 'Couldn\'t find created secret')

    def test_creating_secret_w_bit_length_str(self):
        resps = self.behaviors.create_and_check_secret(bit_length=512)
        secret = resps['get_resp'].entity
        self.assertEqual(resps['get_resp'].status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 512)

    def test_creating_w_null_entries(self):
        """ Covers case when you push a secret full of nulls. This should
        return a 400.
        - Reported in Barbican GitHub Issue #90
        """
        resp = self.behaviors.create_secret()
        self.assertEqual(resp['status_code'], 400,
                         'Should have failed with 400')

    def test_creating_w_empty_name(self):
        """ When a test is created with an empty or null name attribute, the
         system should return the secret's UUID on a get
         - Reported in Barbican GitHub Issue #89
        """
        c_resp = self.behaviors.create_secret(name=None,
                                              mime_type=self.config.mime_type)

        get_resp = self.client.get_secret(secret_id=c_resp['secret_id'])
        self.assertEqual(get_resp.entity.name,
                         c_resp['secret_id'],
                         'name doesn\'t match UUID of secret')

    def test_creating_w_empty_mime_type(self):
        resps = self.behaviors.create_and_check_secret(mime_type='')
        self.assertEqual(resps['create_resp']['status_code'], 400,
                         'Should have failed with 400')

    def test_creating_w_empty_secret(self):
        resps = self.behaviors.create_and_check_secret(plain_text='')
        self.assertEqual(resps['create_resp']['status_code'], 400,
                         'Should have failed with 400')

    def test_creating_w_oversized_secret(self):
        """
        Current size limit is 10k bytes. Beyond that it should return 413
        """
        data = bytearray().zfill(10001)

        resps = self.behaviors.create_and_check_secret(plain_text=str(data))
        self.assertEqual(resps['create_resp']['status_code'], 413,
                         'Should have failed with 413')

    def test_creating_w_invalid_mime_type(self):
        resps = self.behaviors.create_and_check_secret(mime_type='crypto/boom')
        self.assertEqual(resps['create_resp']['status_code'], 400,
                         'Should have failed with 400')

    def test_getting_secret_that_doesnt_exist(self):
        resp = self.client.get_secret('not_a_uuid')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    def test_getting_secret_data_w_invalid_mime_type(self):
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        resp = self.client.get_secret(resp['secret_id'], mime_type='i/m')
        self.assertEqual(resp.status_code, 406, 'Should have failed with 406')

    def test_creating_w_plain_text_as_array(self):
        resps = self.behaviors.create_and_check_secret(plain_text=['boom'])
        self.assertEqual(resps['create_resp']['status_code'], 400,
                         'Should have failed with 400')

    def test_paging_limit_and_offset(self):
        # Create secret pool
        for count in range(1, 20):
            self.behaviors.create_secret_from_config(use_expiration=False)

        # First set of secrets
        resp = self.client.get_secrets(limit=10, offset=0)
        sec_group1 = resp.entity

        # Second set of secrets
        resp = self.client.get_secrets(limit=20, offset=10)
        sec_group2 = resp.entity

        duplicates = [secret for secret in sec_group1.secrets
                      if secret in sec_group2.secrets]

        self.assertEqual(len(sec_group1.secrets), 10)
        self.assertGreaterEqual(len(sec_group2.secrets), 1)
        self.assertEqual(len(duplicates), 0,
                         'Using offset didn\'t return unique secrets')
