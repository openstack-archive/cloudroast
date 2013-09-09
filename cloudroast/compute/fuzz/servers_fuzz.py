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

from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound
from cloudroast.compute.fixtures import (ComputeFixture,
                                         FlavorIdNegativeDataList,
                                         ImageIdNegativeDataList,
                                         ServerIdNegativeDataList)


@DataDrivenFixture
class FuzzServersAPI(ComputeFixture):

    @data_driven_test(dataset_source=ServerIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_get_server(self, server_id=None):
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(server_id)

    @data_driven_test(dataset_source=ServerIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_delete_server(self, server_id=None):
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server(server_id)

    @data_driven_test(dataset_source=FlavorIdNegativeDataList())
    @tags(type='negative', net='no')
    def test_create_server_with_unknown_flavor(self, flavor_id):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                'testserver', self.image_ref, flavor_id)

    @data_driven_test(dataset_source=ImageIdNegativeDataList())
    @tags(type='negative', net='no')
    def test_create_server_with_unknown_image(self, image_id):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                'testserver', image_id, self.flavor_ref)
