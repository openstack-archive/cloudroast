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
from test_repo.cloudkeep.barbican.fixtures import SecretsFixture


class SecretsAPI(SecretsFixture):

    def test_adding_full_secret(self):
        """ Covers proper creation of secret with an expiration attribute set
        - Reported in Barbican GitHub Issue #76
        """
        resp = self.behaviors.create_secret_from_config()

        self.assertEqual(resp['status_code'], 201)
        self.assertGreater(len(resp['secret_id']), 0)

    def test_adding_secret_wout_expiration(self):
        resp = self.behaviors.create_secret_from_config(use_expiration=False)

        self.assertEqual(resp['status_code'], 201)
        self.assertGreater(len(resp['secret_id']), 0)

    def test_get_secret_metadata(self):
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        self.assertEqual(resp['status_code'], 201)

        sec_resp = self.client.get_secret(secret_id=resp['secret_id'])
        metadata = sec_resp.entity

        self.assertEqual(sec_resp.status_code, 200)
        self.assertEqual(metadata.status, 'ACTIVE')
        self.assertEqual(metadata.name, self.config.name)
        self.assertEqual(metadata.cypher_type, self.config.cypher_type)
        self.assertEqual(metadata.algorithm, self.config.algorithm)
        self.assertEqual(metadata.bit_length, self.config.bit_length)

    def test_get_secret(self):
        resp = self.behaviors.create_secret_from_config(use_expiration=False)
        self.assertEqual(resp['status_code'], 201)

        sec_resp = self.client.get_secret(secret_id=resp['secret_id'],
                                          mime_type=self.config.mime_type)
        self.assertEqual(sec_resp.status_code, 200)
        self.assertIn(self.config.plain_text, sec_resp.content)

    def test_updating_a_secret(self):
        # Create
        resp = self.behaviors.create_secret_from_config(use_expiration=False,
                                                        use_plain_text=False)
        self.assertEqual(resp['status_code'], 201)

        # Update
        update_resp = self.client.add_secret_plain_text(
            secret_id=resp['secret_id'],
            mime_type=self.config.mime_type,
            plain_text='testing_update_secret')
        self.assertEqual(update_resp.status_code, 200)

        # Get/Check Updated
        sec_resp = self.client.get_secret(secret_id=resp['secret_id'],
                                          mime_type=self.config.mime_type)
        self.assertIn('testing_update_secret', sec_resp.content)

    def test_deleting_a_secret(self):
        resp = self.behaviors.create_secret_from_config(use_expiration=False,
                                                        use_plain_text=False)
        self.assertEqual(resp['status_code'], 201)

        del_resp = self.behaviors.delete_secret(resp['secret_id'])
        self.assertEqual(del_resp.status_code, 200)

    def test_get_secrets(self):
        # Make sure we have at least one secret to list
        self.behaviors.create_secret_from_config(use_expiration=False)
        get_resp = self.client.get_secrets()
        self.assertEqual(get_resp.status_code, 200)

        secrets = get_resp.entity.secrets
        self.assertGreater(len(secrets), 0)
