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
from cloudcafe.compute.common.exceptions import ActionInProgress
from cloudroast.compute.fixtures import ComputeAdminFixture


class CreateFlavorTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateFlavorTest, cls).setUpClass()
        cls.flavor_name = rand_name('flavor')
        cls.flavor = cls.admin_flavors_client.create_flavor(
            name=cls.flavor_name, ram='64', vcpus='1', disk='10',
            is_public=True).entity

    @classmethod
    def tearDownClass(cls):
        super(CreateFlavorTest, cls).tearDownClass()
        cls.admin_flavors_client.delete_flavor(cls.flavor.id)

    @tags(type='positive', net='no')
    def test_create_server_from_new_flavor(self):
        resp = self.server_behaviors.create_active_server(
            flavor_ref=self.flavor.id)
        server = resp.entity
        self.resources.add(server.id, self.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_create_flavor_with_duplicate_id(self):
        with self.assertRaises(ActionInProgress):
            self.admin_flavors_client.create_flavor(
                name=self.flavor_name, ram='64', vcpus='1', disk='10',
                id=self.flavor.id, is_public=True)
