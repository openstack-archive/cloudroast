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
from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.objectstorage.generators import ObjectDatasetList


@DataDrivenFixture
class QuickTest(ObjectStorageFixture):
    def test_create_container(self):
        response = self.client.create_container('quick_test_container')
        self.assertTrue(response.ok)

        response = self.client.delete_container('quick_test_container')
        self.assertTrue(response.ok)

    @data_driven_test(ObjectDatasetList())
    def ddtest_create_object(self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor='quick_test_container')
        object_name = Constants.VALID_OBJECT_NAME
        generate_object(container_name, object_name)

        response = self.client.get_object(container_name, object_name)
        self.assertEqual(200, response.status_code, 'should return object')
