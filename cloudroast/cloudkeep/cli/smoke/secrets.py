"""
Copyright 2014 Rackspace

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
from cafe.drivers.unittest.decorators import tags
from cloudroast.cloudkeep.cli.fixtures import SecretsCLIFixture


class SecretsCLISmokeTests(SecretsCLIFixture):

    @tags('smoke', 'cli')
    def test_create_secret(self):
        hateos_ref, resp = self.behavior.store_secret(name='test')
        self.assertEqual(resp.return_code, 0)
        self.assertGreater(len(hateos_ref), 0)

    @tags('smoke', 'cli')
    def test_delete_secret(self):
        hateos_ref, resp = self.behavior.store_secret(name='test', clean=False)
        resp = self.client.delete(hateos_ref)
        self.assertEqual(resp.return_code, 0)

    @tags('smoke', 'cli')
    def test_get_secret(self):
        hateos_ref, resp = self.behavior.store_secret(name='test')
        self.assertEqual(resp.return_code, 0)

        get_resp = self.client.get(hateos_ref)
        secret = get_resp.entity

        self.assertIsNotNone(secret)
        self.assertEqual(secret.name, 'test')

    @tags('smoke', 'cli')
    def test_get_secret_list(self):
        # Create 10 secrets to capture
        for i in range(10):
            hateos_ref, resp = self.behavior.store_secret(name='test')
            self.assertEqual(resp.return_code, 0)

        resp = self.client.list_secrets()
        secret_list = resp.entity

        self.assertIsNotNone(secret_list)
        self.assertEqual(len(secret_list), 10)
