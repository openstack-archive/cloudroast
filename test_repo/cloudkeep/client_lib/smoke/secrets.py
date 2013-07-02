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


class SecretsAPI(SecretsFixture):

    def test_cl_create_secret(self):
        """Covers creating a secret with the barbicanclient library.
        Includes creating a secret with an expiration.
        - Reported in python-barbicanclient GitHub Issue #9
        """
        try:
            secret = self.cl_behaviors.create_secret_from_config(
                use_expiration=True)

            resp = self.barb_client.get_secret(secret.id)
            self.assertEqual(resp.status_code, 200,
                             'Barbican returned bad status code')
        except TypeError, error:
            self.fail("Failed with TypeError: %s" % error)

    def test_cl_create_secret_wout_expiration(self):
        """Covers creating a secret without expiration with
        barbicanclient library.
        """
        resps = self.cl_behaviors.create_and_check_secret()
        self.assertEqual(resps['get_resp'].status_code, 200,
                         'Barbican returned bad status code')

    def test_cl_get_secret_by_href(self):
        """Covers getting a secret by href with barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)

        secret = self.cl_client.get_secret(href=resp['secret_ref'])
        self.assertIsNotNone(secret)

    def test_cl_get_secret_by_id(self):
        """Covers getting a secret by id with barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')
        secret = self.cl_client.get_secret_by_id(secret_id=resp['secret_id'])
        self.assertIsNotNone(secret)

    def test_cl_delete_secret_by_href(self):
        """Covers deleting a secret by href with barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        self.cl_behaviors.delete_secret(secret_ref=resp['secret_ref'])
        # Deleting here because using two different behaviors
        self.barb_behaviors.remove_from_created_secrets(
            secret_id=resp['secret_id'])

        get_resp = self.barb_client.get_secret(secret_id=resp['secret_id'])
        self.assertEqual(get_resp.status_code, 404,
                         'Should have failed with 404')

    def test_cl_delete_secret_by_id(self):
        """Covers deleting a secret by id with barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        self.cl_behaviors.delete_secret_by_id(secret_id=resp['secret_id'])
        # Deleting here because using two different behaviors
        self.barb_behaviors.remove_from_created_secrets(
            secret_id=resp['secret_id'])

        get_resp = self.barb_client.get_secret(secret_id=resp['secret_id'])
        self.assertEqual(get_resp.status_code, 404,
                         'Should have failed with 404')

    def test_cl_list_secrets(self):
        """Covers listing secrets with barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        list_tuple = self.cl_client.list_secrets(limit=10, offset=0)
        secrets = list_tuple[0]
        self.assertGreater(len(secrets), 0)

    def test_cl_list_secrets_by_href(self):
        """Covers listing secrets by href with barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        list_tuple = self.cl_client.list_secrets_by_href()
        secrets = list_tuple[0]
        self.assertGreater(len(secrets), 0)

    def test_cl_create_secret_metadata(self):
        """Covers creating a secret with barbicanclient library and checking
        the metadata of the secret.
        """
        secret = self.cl_behaviors.create_secret_from_config(
            use_expiration=False)

        resp = self.barb_client.get_secret(secret.id)
        metadata = resp.entity

        self.assertEqual(resp.status_code, 200, 'Returned bad status code')
        self.assertEqual(metadata.status, 'ACTIVE')
        self.assertEqual(metadata.name, self.config.name)
        self.assertEqual(metadata.cypher_type, self.config.cypher_type)
        self.assertEqual(metadata.algorithm, self.config.algorithm)
        self.assertEqual(metadata.bit_length, self.config.bit_length)

    def test_cl_get_raw_secret_by_href(self):
        """Covers getting the secret payload by href with
        barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        raw_secret = self.cl_client.get_raw_secret(
            resp['secret_ref'], self.config.mime_type)

        self.assertEqual(raw_secret, self.config.plain_text)

    def test_cl_get_raw_secret_by_id(self):
        """Covers getting the secret payload by id with
        barbicanclient library.
        """
        resp = self.barb_behaviors.create_secret_from_config(
            use_expiration=False)
        self.assertEqual(resp['status_code'], 201,
                         'Barbican returned bad status code')

        raw_secret = self.cl_client.get_raw_secret_by_id(
            resp['secret_id'], self.config.mime_type)

        self.assertEqual(raw_secret, self.config.plain_text)
