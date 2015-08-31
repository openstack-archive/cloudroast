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

from time import sleep

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
CONTAINER_NAME = 'container_quota_test_container'


class ContainerQuotaTest(ObjectStorageFixture):
    def tearDown(self):
        self.behaviors.force_delete_containers([CONTAINER_NAME])

    def test_set_container_quota_bytes_header(self):
        """
        Scenario:
        'X-Container-Meta-Quota-Bytes' is set on a container

        Expected Results:
        container HEAD request returns the
        'X-Container-Meta-Quota-Bytes' header and it is set
        properly
        """
        container_bytes = '1024'
        hdrs = {'X-Container-Meta-Quota-Bytes': container_bytes}
        response = self.client.create_container(CONTAINER_NAME, headers=hdrs)

        self.assertTrue(
            response.ok,
            msg=("container created with x-container-meta-quota-bytes"
                 " header returned status code {0}").format(
                response.status_code))

        response = self.client.get_container_metadata(CONTAINER_NAME)

        expected = container_bytes
        received = response.headers.get('x-container-meta-quota-bytes')

        self.assertEqual(
            expected,
            received,
            msg=("x-container-meta-quota-bytes header was not set properly."
                 " expected: {0} received: {1}").format(expected, received))

    def test_set_container_quota_count_header(self):
        """
        Scenario:
        'X-Container-Meta-Quota-Count' is set on a container

        Expected Results:
        container HEAD request returns the
        'X-Container-Meta-Quota-Count' header and it is set
        properly
        """
        obj_limit = '10'
        hdrs = {'X-Container-Meta-Quota-Count': obj_limit}
        self.client.create_container(CONTAINER_NAME, headers=hdrs)
        response = self.client.get_container_metadata(CONTAINER_NAME)

        self.assertTrue(
            response.ok,
            msg=("container created with x-container-meta-quota-count"
                 " header returned status code {0}").format(
                response.status_code))

        expected = obj_limit
        received = response.headers.get('x-container-meta-quota-count')

        self.assertEqual(
            expected,
            received,
            msg=("x-container-meta-quota-count header was not set properly."
                 " expected: {0} received: {1}").format(expected, received))

    def test_bad_container_quota_headers(self):
        """
        Scenario:
        Set bad quota headers

        Expected Results:
        bad request status is returned
        """
        # create a container and set a bad quota count header
        hdrs = {'X-Container-Meta-Quota-Count': 'drok'}
        response = self.client.create_container(CONTAINER_NAME, headers=hdrs)

        self.assertEqual(response.status_code, 400)

        # create a container and set a bad quota bytes header
        hdrs = {'X-Container-Meta-Quota-Bytes': 'drok'}
        response = self.client.create_container(CONTAINER_NAME, headers=hdrs)

        self.assertEqual(response.status_code, 400)

    def test_container_quota_count(self):
        """
        Scenario:
        'X-Container-Meta-Quota-Count' is set on a container.
        objects are created in the container == the container limit.
        an object is created to exceed the container limit.

        Expected Results:
        objects created <= the container limit function properly reflecting
        the correct count in the 'x-container-object-count' header and the
        actual container listing.

        objects created > the container limit will send the correct error
        status code. the object will not be created and the
        'x-container-object-count' will not be incremented.
        """
        # create a container and set the obj limit
        obj_limit = 10
        hdrs = {'X-Container-Meta-Quota-Count': str(obj_limit)}
        self.client.create_container(CONTAINER_NAME, headers=hdrs)

        # create objects == the set limit
        headers = \
            {'Content-Length': str(len(Constants.VALID_OBJECT_DATA)),
             'Content-Type': CONTENT_TYPE_TEXT}

        for num in range(obj_limit):
            response = self.client.create_object(
                CONTAINER_NAME,
                "obj_{0}".format(str(num)),
                headers=headers,
                data=Constants.VALID_OBJECT_DATA)
            self.assertTrue(
                response.status_code,
                msg=("obj_{0} was not created. obj creation returned"
                     " status code {1}").format(str(num),
                                                str(response.status_code)))

        # check the obj count in the header and body of the container listing
        response = self.client.list_objects(CONTAINER_NAME)

        self.assertEqual(
            str(obj_limit),
            response.headers.get('x-container-object-count'),
            msg="x-container-object-count header expected: {0} received"
                "{1}".format(
                str(obj_limit),
                str(response.headers.get('x-container-object-count'))))

        obj_count = 0
        if response.entity:
            obj_count = len(response.entity)

        self.assertEqual(
            obj_limit,
            obj_count,
            msg="container list expected: {0} received {1}".format(
                str(obj_limit),
                str(obj_count)))

        # create an object to exceed the container obj limit
        response = self.client.create_object(
            CONTAINER_NAME,
            "obj_{0}".format(str(obj_limit)),
            headers=headers,
            data=Constants.VALID_OBJECT_DATA)

        # check to see that the obj creation returns the correct status code
        self.assertEqual(
            413,
            response.status_code,
            msg="obj creation expected status code: {0} received {1}".format(
                '413',
                str(response.status_code)))

        # check the obj count in the header and body of the container listing
        response = self.client.list_objects(CONTAINER_NAME)

        self.assertEqual(
            str(obj_limit),
            response.headers.get('x-container-object-count'),
            msg="x-container-object-count header expected: {0} received"
                "{1}".format(
                str(obj_limit),
                str(response.headers.get('x-container-object-count'))))

        obj_count = 0
        if response.entity:
            obj_count = len(response.entity)

        self.assertEqual(
            obj_limit,
            obj_count,
            msg="container list expected: {0} received {1}".format(
                str(obj_limit),
                str(obj_count)))

    def test_container_quota_bytes(self):
        """
        Scenario:
        'X-Container-Meta-Quota-Bytes' is set on a container.
        an obj is created in the container == the byte limit of the container.
        an object is created to exceed the byte limit of the container.

        Expected Results:
        objects created <= the container limit function properly reflecting
        the correct count in the 'x-container-object-count' header and the
        actual container listing.

        objects created > the container byte limit will send the correct error
        status code. the object will not be created and the
        'x-container-object-count' will not be incremented.
        'x-container-object-bytes' will not be incremented.
        """
        data_string = "0123456789"

        # create a container and set the obj limit
        hdrs = {'X-Container-Meta-Quota-Bytes': str(len(data_string))}
        self.client.create_container(CONTAINER_NAME, headers=hdrs)

        # create object == the set limit
        headers = \
            {'Content-Length': str(len(data_string)),
             'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            CONTAINER_NAME,
            "obj_1",
            headers=headers,
            data=data_string)

        # check to see that the obj creation returns the correct status code
        self.assertTrue(
            response.ok,
            msg=("obj_1 was not created. obj creation returned"
                 " status code {0}").format(str(response.status_code)))

        # this sleep is for CF eventual consistency
        sleep(60)

        response = self.client.create_object(
            CONTAINER_NAME,
            "obj_2",
            headers=headers,
            data=data_string)

        # check to see that the obj creation returns the correct failure code
        self.assertEqual(
            413,
            response.status_code,
            msg="obj creation expected status code: {0} received {1}".format(
                '413',
                str(response.status_code)))

        response = self.client.list_objects(CONTAINER_NAME)

        self.assertEqual(
            '1',
            response.headers.get('x-container-object-count'),
            msg="x-container-object-count header expected: {0} received"
                "{1}".format(
                '1',
                str(response.headers.get('x-container-object-count'))))

        obj_count = 0
        if response.entity:
            obj_count = len(response.entity)

        self.assertEqual(
            1,
            obj_count,
            msg="container list expected: {0} received {1}".format(
                '1',
                str(obj_count)))

        self.assertEqual(
            str(len(data_string)),
            response.headers.get('x-container-bytes-used'),
            msg="x-container-bytes-used header expected: {0} received"
                "{1}".format(
                str(len(data_string)),
                str(response.headers.get('x-container-object-count'))))
