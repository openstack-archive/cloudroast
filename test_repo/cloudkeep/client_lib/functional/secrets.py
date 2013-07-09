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
from test_repo.cloudkeep.client_lib.fixtures import SecretsFixture
from barbicanclient.common.exceptions import ClientException


class SecretsAPI(SecretsFixture):

    def test_cl_create_secret_w_only_mime_type(self):
        """Covers creating secret with only required fields. In this case,
        only mime type is required.
        """
        secret = self.cl_behaviors.create_secret(
            mime_type=self.config.mime_type)

        resp = self.barb_client.get_secret(secret.id)
        self.assertEqual(resp.status_code, 200,
                         'Barbican returned bad status code')

    def test_cl_create_secret_w_null_values(self):
        """Covers creating secret with all null values. Should raise a
        ClientException.
        """
        self.assertRaises(ClientException, self.cl_behaviors.create_secret)

    def test_cl_create_secret_w_null_name(self):
        """Covers creating secret with a null name."""
        secret = self.cl_behaviors.create_secret(
            name=None, mime_type=self.config.mime_type)
        self.assertIsNotNone(secret)

    def test_cl_create_secret_w_empty_name(self):
        """Covers creating secret with an empty name."""
        secret = self.cl_behaviors.create_secret(
            name='', mime_type=self.config.mime_type)
        self.assertIsNotNone(secret)

    def test_cl_create_secret_w_null_name_checking_name(self):
        """Covers creating secret with a null name, checking that the name
        matches the secret ID.
        """
        secret = self.cl_behaviors.create_secret(
            name=None, mime_type=self.config.mime_type)
        self.assertEqual(secret.name, secret.id,
                         "Name did not match secret ID")

    def test_cl_create_secret_w_empty_name_checking_name(self):
        """Covers creating secret with an empty name, checking that the name
        matches the secret ID.
        """
        secret = self.cl_behaviors.create_secret(
            name='', mime_type=self.config.mime_type)
        self.assertEqual(secret.name, secret.id,
                         "Name did not match secret ID")

    def test_cl_create_secret_w_empty_secret(self):
        """Covers creating secret with an empty String as the plain-text value.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret,
                          mime_type=self.config.mime_type,
                          plain_text='')

    def test_cl_create_secret_w_invalid_mime_type(self):
        """Covers creating secret with an invalid mime type.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret_overriding_cfg,
                          mime_type='crypto/boom')

    def test_cl_create_secret_w_data_as_array(self):
        """Covers creating secret with the secret data as an array.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret_overriding_cfg,
                          plain_text=['boom'])

    def test_cl_create_secret_w_invalid_bit_length(self):
        """Covers creating secret with a bit length that is not an integer.
        Should raise a ClientException.
        - Reported in python-barbicanclient GitHub Issue #11
        """
        try:
            self.assertRaises(ClientException,
                              self.cl_behaviors.create_secret_overriding_cfg,
                              bit_length='not-an-int')
        except ValueError, error:
            self.fail("Failed with ValueError: {0}".format(error))

    def test_cl_create_secret_w_negative_bit_length(self):
        """Covers creating secret with a negative bit length.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret_overriding_cfg,
                          bit_length=-1)

    def test_cl_create_secret_w_oversized_data(self):
        """Covers creating secret with secret data that is greater than
        the limit of 10k bytes. Should raise a ClientException.
        """
        data = bytearray().zfill(10001)
        data = data.decode("utf-8")
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_secret_overriding_cfg,
                          plain_text=data)

    def test_cl_delete_nonexistent_secret_by_ref(self):
        """Covers deleting a secret that doesn't exist by href.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_client.delete_secret,
                          href='invalid-ref')

    def test_cl_delete_nonexistent_secret_by_id(self):
        """Covers deleting a secret that doesn't exist by id.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_client.delete_secret_by_id,
                          secret_id='invalid-id')

    def test_cl_get_nonexistent_by_href(self):
        """Covers getting a secret that doesn't exist by href.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_client.get_secret,
                          href='invalid-ref')

    def test_cl_get_nonexistent_by_id(self):
        """Covers getting a secret that doesn't exist by id.
        Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_client.get_secret_by_id,
                          secret_id='invalid-id')

    def test_cl_get_secret_checking_metadata_by_href(self):
        """Covers getting a secret by href and checking the secret metadata."""
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        secret = self.cl_client.get_secret(resp['secret_ref'])

        self.assertEqual(secret.status, 'ACTIVE')
        self.assertEqual(secret.name, self.config.name)
        self.assertEqual(secret.mime_type, self.config.mime_type)
        self.assertEqual(secret.cypher_type, self.config.cypher_type)
        self.assertEqual(secret.algorithm, self.config.algorithm)
        self.assertEqual(secret.bit_length, self.config.bit_length)

    def test_cl_get_secret_checking_metadata_by_id(self):
        """Covers getting a secret by id and checking the secret metadata."""
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        secret = self.cl_client.get_secret_by_id(resp['secret_id'])

        self.assertEqual(secret.status, 'ACTIVE')
        self.assertEqual(secret.name, self.config.name)
        self.assertEqual(secret.mime_type, self.config.mime_type)
        self.assertEqual(secret.cypher_type, self.config.cypher_type)
        self.assertEqual(secret.algorithm, self.config.algorithm)
        self.assertEqual(secret.bit_length, self.config.bit_length)

    def test_cl_get_raw_secret_by_href_w_nonexistent_secret(self):
        """Covers getting the encrypted data of a nonexistent secret
        by href. Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_client.get_raw_secret,
                          href='not-an-href',
                          mime_type='mime-type')

    def test_cl_get_raw_secret_by_id_w_nonexistent_secret(self):
        """Covers getting the encrypted data of a nonexistent secret
        by id. Should raise a ClientException.
        """
        self.assertRaises(ClientException,
                          self.cl_client.get_raw_secret_by_id,
                          secret_id='not-an-id',
                          mime_type='mime-type')

    def test_cl_get_empty_raw_secret_by_href(self):
        """Covers getting the encrypted data of an empty secret
        by href. Should raise a ClientException.
        """
        resp = self.barb_behaviors.create_secret(
            mime_type=self.config.mime_type)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        self.assertRaises(ClientException,
                          self.cl_client.get_raw_secret,
                          href=resp['secret_ref'],
                          mime_type=self.config.mime_type)

    def test_cl_get_empty_raw_secret_by_id(self):
        """Covers getting the encrypted data of an empty secret
        by id. Should raise a ClientException.
        """
        resp = self.barb_behaviors.create_secret(
            mime_type=self.config.mime_type)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        self.assertRaises(ClientException,
                          self.cl_client.get_raw_secret_by_id,
                          secret_id=resp['secret_id'],
                          mime_type=self.config.mime_type)
