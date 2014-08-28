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
STATUS_CODE_MSG = ('{method} expected status code {expected}'
                   ' received status code {received}')


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
    def ddtest_object_creation_with_x_delete_after(
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_x_delete_after_with_unicode_container_name(
            self, object_type, generate_object):
        """
        Scenario:
            Create a container with a unicode name and then add
            an expiring object to it using x_delete_after

        Expected Results:
            The object should be available until the expiration time,
            then it should be deleted
        """
        delete_after = 60

        container_description = unicode(u'\u262D\u2622').encode('utf-8')
        container_name = self.create_temp_container(
            descriptor=container_description)

        object_name = self.default_obj_name
        object_headers = {'X-Delete-After': delete_after}
        generate_object(container_name,
                        object_name,
                        headers=object_headers)

        object_response = self.client.get_object(container_name, object_name)

        method = 'Creating Expiring Object in Unicode Container'
        expected = 200
        received = object_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        # Sleep for period set as X-Delete-After(object expiration)
        time.sleep(delete_after)

        object_response = self.client.get_object(container_name, object_name)

        method = 'GET on expired object in Unicode Container'
        expected = 404
        received = object_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_x_delete_at_with_unicode_container_name(
            self, object_type, generate_object):
        """
        Scenario:
            Create a container with a unicode name and then add
            an expiring object to it using x_delete_at.

        Expected Results:
            The object should be available until the expiration time,
            then it should be deleted
        """
        start_time = calendar.timegm(time.gmtime())
        future_time = str(int(start_time + 60))

        container_description = unicode(u'\u262D\u2622').encode('utf-8')
        container_name = self.create_temp_container(
            descriptor=container_description)

        object_name = self.default_obj_name
        object_headers = {'X-Delete-At': future_time}
        generate_object(container_name,
                        object_name,
                        headers=object_headers)

        object_response = self.client.get_object(container_name, object_name)

        method = 'Creating Expiring Object in Unicode Container'
        expected = 200
        received = object_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        # Wait for object to expire using interval from config
        time.sleep(
            self.objectstorage_api_config.object_deletion_wait_interval)

        object_response = self.client.get_object(container_name, object_name)

        method = 'GET on expired object in Unicode Container'
        expected = 404
        received = object_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))
