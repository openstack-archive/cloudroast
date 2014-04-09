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
import calendar
import time

from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.objectstorage.generators import ObjectDatasetList

CONTAINER_DESCRIPTOR = 'expiring_object_test'


@DataDrivenFixture
class ExpiringObjectTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ExpiringObjectTest, cls).setUpClass()
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.default_obj_data = "Test Data"

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_x_delete_at(self, object_type,
                                                generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name

        start_time = calendar.timegm(time.gmtime())
        future_time = str(int(start_time + 60))
        object_headers = {'X-Delete-At': future_time}
        generate_object(container_name, object_name, headers=object_headers)

        response = self.client.get_object(container_name, object_name)

        content_length = response.headers.get('content-length')
        self.assertNotEqual(content_length, 0)

        # wait for the object to expire - future_time + 10 seconds
        time.sleep(70)

        response = self.client.get_object(container_name, object_name)

        self.assertEqual(response.status_code, 404)

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_delete_after(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {'X-Delete-After': '60'}
        generate_object(container_name, object_name, headers=object_headers)

        response = self.client.get_object(container_name, object_name)

        content_length = response.headers.get('content-length')
        self.assertNotEqual(content_length, 0)

        # wait for the object to expire - delete after 60 seconds + 10 seconds
        time.sleep(70)

        response = self.client.get_object(container_name, object_name)

        self.assertEqual(response.status_code, 404)
