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

from test_repo.compute.fixtures import ComputeFixture

class FlavorsTest(ComputeFixture):

    def test_create_delete_keypair(self):
        resp = self.keypairs_client.create_keypair('test3')
        self.assertEqual(resp.status_code, 200)

        keypair = resp.entity
        self.assertEqual(keypair.name, 'test3')
        self.assertIsNotNone(keypair.public_key)
        self.assertIsNotNone(keypair.fingerprint)

        self.keypairs_client.list_keypairs()

        self.keypairs_client.delete_keypair('test3')

