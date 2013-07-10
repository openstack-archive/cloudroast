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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.compute.common.exceptions import ItemNotFound
from test_repo.compute.fixtures import ComputeFixture


class DeleteKeypairTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteKeypairTest, cls).setUpClass()
        cls.name = rand_name("key")
        cls.keypair = cls.keypairs_client.create_keypair(cls.name).entity
        cls.delete_resp = cls.keypairs_client.delete_keypair(cls.name)

    @tags(type='positive', net='no')
    def test_delete_keypair_response(self):
        self.assertEqual(self.delete_resp.status_code, 202)

    @tags(type='positive', net='no')
    def test_deleted_keypair_not_listed(self):
        keypairs_list = self.keypairs_client.list_keypairs().entity
        self.assertNotIn(self.keypair, keypairs_list)

    @tags(type='negative', net='no')
    def test_get_deleted_keypair_fails(self):
        with self.assertRaises(ItemNotFound):
            self.keypairs_client.get_keypair(self.name)

    @tags(type='negative', net='no')
    def test_delete_deleted_keypair_fails(self):
        with self.assertRaises(ItemNotFound):
            self.keypairs_client.delete_keypair(self.name)
