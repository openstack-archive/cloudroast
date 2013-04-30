from test_repo.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import randomstring as randstring

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
STATUS_CODE_MSG = '{method} expected status code {expected}' \
    ' received status code {received}'


class ContainerSmokeTest(ObjectStorageFixture):
    """4.2.1. List Objects in a Container"""
    def test_objects_list_with_non_empty_container(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.list_objects(container_name)

        method = 'list storage objects with non empty container'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.2.1.1. Serialized List Output"""
    def test_objects_list_with_format_json_query_parameter(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        format_ = {'format': 'json'}

        response = self.client.list_objects(container_name, params=format_)

        method = 'list storage objects with format json query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_objects_list_with_format_xml_query_parameter(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        format_ = {'format': 'xml'}

        response = self.client.list_objects(container_name, params=format_)

        method = 'list storage objects with format xml query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_list_with_accept_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Accept': '*/*'}

        response = self.client.list_objects(
            container_name,
            headers=headers)

        method = 'list storage objects with accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_list_with_text_accept_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Accept': 'text/plain'}

        response = self.client.list_objects(
            container_name,
            headers=headers)

        method = 'list storage objects with text accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_list_with_json_accept_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Accept': 'application/json'}

        response = self.client.list_objects(
            container_name,
            headers=headers)

        method = 'list storage objects with json accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_list_with_application_xml_accept_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Accept': 'application/xml'}

        response = self.client.list_objects(
            container_name,
            headers=headers)

        method = 'list storage objects with accept application/xml header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_list_with_text_xml_accept_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Accept': 'text/xml'}

        response = self.client.list_objects(
            container_name,
            headers=headers)

        method = 'list storage objects with accept text/xml header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.2.1.2. Controlling a Large List of Objects"""
    def test_objects_list_with_limit_query_parameter(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        limit = {'limit': '3'}

        response = self.client.list_objects(container_name, params=limit)

        method = 'list storage objects with limit query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_objects_list_with_marker_query_parameter(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        marker = {'marker': container_name}

        response = self.client.list_objects(container_name, params=marker)

        method = 'list storage objects with marker query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.2.1.3. Pseudo-Hierarchical Folders/Directories"""
    def test_objects_list_with_prefix_query_parameter(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        prefix = {'prefix': container_name[0:3]}
        response = self.client.list_objects(container_name, params=prefix)

        method = 'list storage objects with prefix query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

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
            foo/object1.txt
            foo/bar/
    """
    def test_objects_list_with_path_query_parameter(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
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
        object_name_postfix = '{0}_{1}'.format(
            self.base_object_name,
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

        self.assertEqual(
            response.status_code,
            200,
            'should list the simulated directory')

        params = {'path': 'path_test/nested_dir/'}

        response = self.client.list_objects(container_name, params=params)

        method = 'list storage objects with path query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_objects_list_with_delimiter_query_parameter(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name_prefix = 'delimiter_test/'
        object_name_postfix = '{0}_{1}'.format(
            self.base_object_name,
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
        response = self.client.list_objects(container_name, params=params)

        self.assertEqual(
            response.status_code, 200,
            'should list the simulated directory')

        params = {'prefix': object_name_prefix, 'delimiter': '/'}

        response = self.client.list_objects(container_name, params=params)

        method = 'list storage objects with delimeter query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.2.2. Create Container"""
    def test_container_creation_with_valid_container_name(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        response = self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = 'container creation with valid container name'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_creation_with_existing_container_name(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        response = self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        self.assertEqual(response.status_code, 201, 'should be created')

        response = self.client.create_container(container_name)

        method = 'container creation with existing container name'
        expected = 202
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_creation_with_metadata(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        metadata = {'Book-One': 'book_A',
                    'Book-Two': 'book_B'}

        response = self.client.create_container(
            container_name,
            metadata=metadata)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = 'container creation with metadata'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.2.3. Delete Container"""
    def test_container_deletion_with_existing_empty_container(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        response = self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        self.assertEqual(response.status_code, 201, 'should be created')

        response = self.client.delete_container(container_name)

        method = 'container deletion'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.list_objects(container_name)

        self.assertEqual(
            response.status_code,
            404,
            'should not exist after deletion')

    def test_container_deletion_with_non_empty_container(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        response = self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        method = 'container creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.delete_container(container_name)

        method = 'container deletion'
        expected = 409
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.2.4. Retrieve Container Metadata"""
    def test_metadata_retrieval_with_newly_created_container(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        metadata = {'Book-One': 'book_A',
                    'Book-Two': 'book_B'}

        response = self.client.create_container(container_name, metadata)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        self.assertEqual(response.status_code, 201, 'should be created')

        response = self.client.get_container_metadata(container_name)

        method = 'metadata retrieval on container created with metadata'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_metadata_retrieval_after_metadata_update(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        metadata = {'Book-One': 'book_A',
                    'Book-Two': 'book_B'}

        response = self.client.set_container_metadata(
            container_name,
            metadata)

        response = self.client.get_container_metadata(container_name)

        method = 'metadata retrieval after metadata update'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.2.5. Create/Update Container Metadata"""
    def test_metadata_update(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())

        response = self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        metadata = {'Book-One': 'book_A',
                    'Book-Two': 'book_B'}

        response = self.client.set_container_metadata(
            container_name,
            metadata)

        method = 'metadata update on container with no existing metadata'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_metadata_update_with_container_possessing_metadata(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        metadata = {'Book-One': 'book_A',
                    'Book-Two': 'book_B'}

        response = self.client.create_container(container_name, metadata)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        metadata = {'Book-One': 'book_C',
                    'Book-Two': 'book_D'}

        response = self.client.set_container_metadata(
            container_name,
            metadata)

        method = 'metadata update on container with existing metadata'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))
