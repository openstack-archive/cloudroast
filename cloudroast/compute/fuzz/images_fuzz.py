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
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudroast.compute.fixtures import (ComputeFixture,
                                         ImageIdNegativeDataList,
                                         ServerIdNegativeDataList)


@DataDrivenFixture
class FuzzImageAPI(ComputeFixture):

    @data_driven_test(dataset_source=ImageIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_get_image(self, image_id=None):
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image(image_id)

    @data_driven_test(dataset_source=ImageIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_delete_image(self, image_id=None):
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(image_id)

    @data_driven_test(dataset_source=ServerIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_create_image(self, server_id=None):
        with self.assertRaises(ItemNotFound):
            self.servers_client.create_image(server_id, 'test')
