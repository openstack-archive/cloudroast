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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound
from cloudroast.compute.fixtures import ComputeAdminFixture


class PrivateFlavorTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(PrivateFlavorTest, cls).setUpClass()
        cls.flavor_name = rand_name('flavor')
        cls.flavor = cls.admin_flavors_client.create_flavor(
            name=cls.flavor_name, ram='64', vcpus='1', disk='10',
            is_public=False).entity
        cls.admin_flavors_client.add_tenant_access(
            flavor_id=cls.flavor.id, tenant=cls.user_config.tenant_id)

    @classmethod
    def tearDownClass(cls):
        super(PrivateFlavorTest, cls).tearDownClass()
        cls.admin_flavors_client.delete_flavor(cls.flavor.id)

    @tags(type='positive', net='no')
    def test_create_server_with_private_flavor(self):
        resp = self.server_behaviors.create_active_server(
            flavor_ref=self.flavor.id)
        server = resp.entity
        self.resources.add(server.id, self.servers_client.delete_server)

    @tags(type='positive', net='no')
    def test_list_private_flavor(self):
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        self.assertIn(self.flavor, flavors)

    @tags(type='positive', net='no')
    def test_get_private_flavor(self):
        response = self.flavors_client.get_flavor_details(self.flavor.id)
        self.assertEqual(response.status_code, 200)


class PrivateFlavorNegativeTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(PrivateFlavorNegativeTest, cls).setUpClass()
        cls.flavor_name = rand_name('flavor')
        cls.flavor = cls.admin_flavors_client.create_flavor(
            name=cls.flavor_name, ram='64', vcpus='1', disk='10',
            is_public=False).entity

    @tags(type='negative', net='no')
    def test_create_server_without_flavor_permissions_fails(self):
        with self.assertRaises(BadRequest):
            resp = self.server_behaviors.create_active_server(
                flavor_ref=self.flavor.id)
            server = resp.entity
            self.resources.add(server.id, self.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_private_flavor_not_listed_without_permissions(self):
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        self.assertNotIn(self.flavor, flavors)

    @tags(type='negative', net='no')
    def test_get_private_flavor_fails_without_permissions(self):
        with self.assertRaises(ItemNotFound):
            self.flavors_client.get_flavor_details(self.flavor.id)
