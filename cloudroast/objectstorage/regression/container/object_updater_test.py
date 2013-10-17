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
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import randomstring as randstring

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
CONTAINER_NAME = 'container_obj_count_test'


class ObjectUpdaterTest(ObjectStorageFixture):
    def test_x_container_object_count_head_get_equivelent(self):
        get_count = 0
        head_count = 0

        container_name = '{0}_{1}'.format(
            CONTAINER_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.obj_names = ["a_obj", "b_obj", "c_obj", "d_obj", "e_obj", "f_obj"]

        for obj_name in self.obj_names:
            self.behaviors.create_object(
                CONTAINER_NAME,
                obj_name,
                headers=headers,
                data=object_data)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        get_response = self.client.list_objects(container_name)
        head_response = self.client.get_container_metadata(container_name)

        get_count = int(get_response.headers.get('x-container-object-count'))
        head_count = int(head_response.headers.get('x-container-object-count'))

        self.assertEqual(
            get_count,
            head_count,
            msg="GET x-container-object-count: {0} HEAD"
            " x-container-object-count: {1}".format(get_count, head_count))

    def test_x_container_object_count_get_with_update(self):
        initial_get_count = 0
        updated_get_count = 0
        expected_get_count = 0
        container_delta = 0

        container_name = '{0}_{1}'.format(
            CONTAINER_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        get_response = self.client.list_objects(container_name)

        initial_get_count = int(get_response.headers.get(
            'x-container-object-count'))

        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.obj_names = ["a_obj", "b_obj", "c_obj", "d_obj", "e_obj", "f_obj"]

        for obj_name in self.obj_names:
            response = self.client.create_object(
                container_name,
                obj_name,
                headers=headers,
                data=object_data)

            if response.ok:
                container_delta += 1

        self.addCleanup(self.client.force_delete_containers, [container_name])

        expected_get_count = initial_get_count + container_delta

        get_response = self.client.list_objects(container_name)

        updated_get_count = int(get_response.headers.get(
            'x-container-object-count'))

        self.assertEqual(
            expected_get_count,
            updated_get_count,
            msg="GET x-container-object-count expected: {0}"
            " x-container-object-count recieved: {1}".format(
                expected_get_count,
                updated_get_count))

    def test_x_container_object_count_head_with_update(self):
        initial_head_count = 0
        updated_head_count = 0
        expected_head_count = 0
        container_delta = 0

        container_name = '{0}_{1}'.format(
            CONTAINER_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        head_response = self.client.get_container_metadata(container_name)

        initial_head_count = int(head_response.headers.get(
            'x-container-object-count'))

        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.obj_names = ["a_obj", "b_obj", "c_obj", "d_obj", "e_obj", "f_obj"]

        for obj_name in self.obj_names:
            response = self.client.create_object(
                container_name,
                obj_name,
                headers=headers,
                data=object_data)

            if response.ok:
                container_delta += 1

        self.addCleanup(self.client.force_delete_containers, [container_name])

        expected_head_count = initial_head_count + container_delta

        head_response = self.client.get_container_metadata(container_name)

        updated_head_count = int(head_response.headers.get(
            'x-container-object-count'))

        self.assertEqual(
            expected_head_count,
            updated_head_count,
            msg="HEAD x-container-object-count expected: {0}"
            " x-container-object-count recieved: {1}".format(
                expected_head_count,
                updated_head_count))
