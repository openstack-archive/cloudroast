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
from binascii import a2b_base64 as base64

from cafe.drivers.unittest.decorators import tags
from cloudcafe.cloudkeep.common.states import SecretsStates
from cloudroast.cloudkeep.client_lib.fixtures import SecretsFixture


class SecretsAPI(SecretsFixture):

    @tags(type='positive')
    def test_create_secret(self):
        resps = self.cl_behaviors.create_and_check_secret()
        get_response = resps.get_resp

         # Check to see if we received a string with http
        self.assertIn('http', resps.entity)
        self.assertEqual(get_response.status_code, 200)

    @tags(type='positive')
    def test_delete_secret(self):
        # Creating sample secret directly with API
        resp = self.barb_behaviors.create_secret_from_config()
        self.assertEqual(resp.status_code, 201)

        # Delete using client lib
        self.cl_behaviors.delete_secret(secret_ref=resp.ref)

        # Removing from Barbican API behavior as well.
        self.barb_behaviors.remove_from_created_secrets(secret_id=resp.id)

        get_response = self.barb_client.get_secret(secret_id=resp.id)
        self.assertEqual(get_response.status_code, 404)

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

    @tags(type='positive')
    def test_get_secret_raw(self):
        resp = self.barb_behaviors.create_secret_from_config()
        self.assertEqual(resp.status_code, 201)

        raw_secret = self.cl_client.get_raw_secret(
            href=resp.ref, content_type=self.config.payload_content_type)

        self.assertEqual(raw_secret, base64(self.config.payload))

    @tags(type='positive')
    def test_list_secrets(self):
        resp = self.barb_behaviors.create_secret_from_config()
        self.assertEqual(resp.status_code, 201)

        secrets = self.cl_client.list_secrets(limit=1, offset=0)
        self.assertEqual(len(secrets), 1)
