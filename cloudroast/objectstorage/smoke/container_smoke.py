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
CONTAINER_NAME = 'container_smoke_test'
STATUS_CODE_MSG = "{method} expected status code {expected}" \
    " received status code {received}"


class ContainerSmokeTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ContainerSmokeTest, cls).setUpClass()

        cls.container_name = CONTAINER_NAME
        cls.client.create_container(cls.container_name)

        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        cls.obj_names = ["b_obj", "c_obj", "d_obj", "e_obj", "f_obj", "g_obj"]

        for obj_name in cls.obj_names:
            cls.client.create_object(
                cls.container_name,
                obj_name,
                headers=headers,
                data=object_data)

    @classmethod
    def tearDownClass(cls):
        super(ContainerSmokeTest, cls).setUpClass()
        cls.client.force_delete_containers([cls.container_name])

    def test_objects_list_with_non_empty_container(self):
        response = self.client.list_objects(self.container_name)

        method = "list objects"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_format_json_query_parameter(self):
        format_ = {'format': 'json'}

        response = self.client.list_objects(
            self.container_name,
            params=format_)

        method = "list objects with format json query parameter"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_format_xml_query_parameter(self):
        format_ = {'format': 'xml'}

        response = self.client.list_objects(
            self.container_name,
            params=format_)

        method = "list objects with format xml query parameter"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_list_with_accept_header(self):
        headers = {'Accept': '*/*'}

        response = self.client.list_objects(
            self.container_name,
            headers=headers)

        method = "list objects with accept */* header"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_list_with_text_accept_header(self):
        headers = {'Accept': 'text/plain'}

        response = self.client.list_objects(
            self.container_name,
            headers=headers)

        method = "list objects with accept text/plain header"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_list_with_json_accept_header(self):
        headers = {'Accept': 'application/json'}

        response = self.client.list_objects(
            self.container_name,
            headers=headers)

        method = "list objects with accept application/json header"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_list_with_application_xml_accept_header(self):
        headers = {'Accept': 'application/xml'}

        response = self.client.list_objects(
            self.container_name,
            headers=headers)

        method = "list objects with accept application/xml header"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_list_with_text_xml_accept_header(self):
        headers = {'Accept': 'text/xml'}

        response = self.client.list_objects(
            self.container_name,
            headers=headers)

        method = "list objects with accept text/xml header"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_limit_query_parameter(self):
        limit = {'limit': '3'}

        response = self.client.list_objects(self.container_name, params=limit)

        method = "list objects with limit query parameter"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_marker_query_parameter(self):
        marker = {'marker': self.container_name}

        response = self.client.list_objects(self.container_name, params=marker)

        method = "list objects with marker query parameter"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_prefix_query_parameter(self):
        prefix = {'prefix': self.obj_names[0][0:2]}

        response = self.client.list_objects(self.container_name, params=prefix)

        method = "list objects with prefix query parameter"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_delimiter_query_parameter(self):
        params = {'delimiter': '/'}

        response = self.client.list_objects(self.container_name, params=params)

        method = "list objects with delimeter query parameter"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_path_query_parameter(self):
        """
        This is a depricated feature that has little documentation.
        The following things need to be done for the path parameter to work.
          1. For every 'directory' a 'directory marker' must be added as a
            object. The directory marker does not need to contain data, and
            thus can have a length of 0.
            Example:
            If you want a directory 'foo/bar/', you would upload a object
            named 'foo/bar/' to your container.

          2. You must upload your objects, prefixed with the 'directory' path.
            Example:
            If you wanted to create an object in 'foo/' and another in
            'foo/bar/', you would have to name the objects as follows:
                foo/object1.txt
                foo/bar/object2.txt

          3. Once this has been done, you can use the path query string
            parameter to list the objects in the simulated directory structure.
            Example:
            Using the above examples, setting path to 'foo/' should list
            the following:
                foo/objet1.txt
                foo/bar/
        """
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        dir_marker = 'path_test/'

        headers = {'Content-Length': '0'}

        self.client.create_object(
            container_name,
            dir_marker,
            headers=headers)

        dir_marker = 'path_test/nested_dir/'

        headers = {'Content-Length': '0'}

        self.client.create_object(
            container_name,
            dir_marker,
            headers=headers)

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name_prefix = 'path_test/nested_dir/'
        object_name_postfix = 'object_{0}'.format(
            randstring.get_random_string())
        object_name = '{0}{1}'.format(object_name_prefix, object_name_postfix)

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        params = {'path': 'path_test/'}

        response = self.client.list_objects(container_name, params=params)

        method = "simulated directory list"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        params = {'path': 'path_test/nested_dir/'}

        response = self.client.list_objects(container_name, params=params)

        method = "simulated obj in directory list"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_objects_list_with_prefix_delimiter_query_parameters(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name_prefix = 'delimiter_test/'
        object_name_postfix = 'object_{0}'.format(
            randstring.get_random_string())
        object_name = '{0}{1}'.format(object_name_prefix, object_name_postfix)

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        params = {'delimiter': '/'}
        response = self.client.list_objects(self.container_name, params=params)

        method = "simulated directory list"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        params = {'prefix': object_name_prefix, 'delimiter': '/'}

        response = self.client.list_objects(container_name, params=params)

        method = "simulated obj in directory list"
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_container_creation_with_valid_container_name(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        response = self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = "container creation"
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_container_creation_with_existing_container_name(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        response = self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = "container creation"
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.create_container(container_name)

        method = "container creation with existing container name"
        expected = 202
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_container_creation_with_metadata(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        headers = {'X-Container-Meta-Ebooks': 'grok_volumes_1_through_10'}

        response = self.client.create_container(
            container_name,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = "container creation with metadata"
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_container_deletion_with_existing_empty_container(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        response = self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = "container creation"
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.delete_container(container_name)

        method = "delete container"
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.list_objects(container_name)

        method = "obj list on deleted container"
        expected = 404
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_metadata_retrieval_with_newly_created_container(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        headers = {'X-Container-Meta-Ebooks': 'grok_volumes_1_through_10'}
        response = self.client.create_container(
            container_name,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = "container creation"
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_container_metadata(container_name)

        method = "container metadata retrieval"
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_metadata_retrieval_after_setting_metadata(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'X-Container-Meta-Ebooks': 'grok_volumes_1_through_10'}

        response = self.client.set_container_metadata(
            container_name,
            headers=headers)

        response = self.client.get_container_metadata(container_name)

        method = "container metadata retrieval"
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_metadata_update_with_container_possessing_metadata(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)
        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'X-Container-Meta-Ebooks': 'grok_volumes_1_through_10'}

        response = self.client.set_container_metadata(
            container_name,
            headers=headers)

        method = "set container metadata"
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        headers = {'X-Container-Meta-Ebooks': 'drok_volumes_10_through_20'}

        response = self.client.set_container_metadata(
            container_name,
            headers=headers)

        method = "container metadata update"
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))
