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
from calendar import timegm
from time import gmtime, sleep

from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants
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
        cls.default_obj_name = Constants.VALID_OBJECT_NAME
        cls.default_obj_data = Constants.VALID_OBJECT_DATA

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_x_delete_at(self, object_type,
                                                generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name

        start_time = timegm(gmtime())
        future_time = str(int(start_time + 60))
        object_headers = {'X-Delete-At': future_time}
        generate_object(container_name, object_name, headers=object_headers)

        response = self.client.get_object(container_name, object_name)

        content_length = response.headers.get('content-length')
        self.assertNotEqual(content_length, 0)

        # wait for the object to expire - future_time + 10 seconds
        sleep(70)

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
        sleep(70)

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
        sleep(delete_after)

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
        start_time = timegm(gmtime())
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
        sleep(
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_deletion_with_x_delete_at(self, **kwargs):
        """
        Scenario:
            Create an object which has the X-Delete-At metadata.

        Expected Results:
            The object should be accessible before the 'delete at' time.
            The object should not be accessible after the 'delete at' time.
            The object should not be listed after the object expirer has had
                time to run.
        """
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        delete_after = 60
        delete_at = str(int(timegm(gmtime()) + delete_after))
        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'X-Delete-At': delete_at}

        resp = self.client.create_object(
            container_name, self.default_obj_name,
            headers=headers, data=self.default_obj_data)

        self.assertEqual(
            201, resp.status_code,
            'Object should be created with X-Delete-At header.')

        resp = self.client.get_object(container_name, self.default_obj_name)

        self.assertEqual(
            200, resp.status_code,
            'Object should exist before X-Delete-At.')

        # wait for the object to be deleted.
        sleep(self.objectstorage_api_config.object_deletion_wait_interval)

        resp = self.client.get_object(container_name, self.default_obj_name)

        self.assertEqual(
            404, resp.status_code,
            'Object should be deleted after X-Delete-At.')

        # wait for the container listing to be updated
        sleep(self.objectstorage_api_config.object_deletion_wait_interval)

        get_response = self.client.list_objects(container_name)

        self.assertEqual(
            204, get_response.status_code,
            'No content should be returned for the request.')

        self.assertEqual(
            0, int(get_response.headers.get('x-container-object-count')),
            'No objects should be listed in the container. Object count was '
            '{0}'.format(get_response.headers.get('x-container-object-count')))

        self.assertIsNone(get_response.entity,
                          'There should not be a response entity. '
                          'Response entity was {0}'.format(
                              get_response.entity))

        head_response = self.client.get_container_metadata(container_name)

        self.assertEqual(
            0, int(head_response.headers.get('x-container-object-count')),
            'No objects should be listed in the container.')
