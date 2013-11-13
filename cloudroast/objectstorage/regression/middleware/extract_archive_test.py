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
import json
import os

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import randomstring as randstring
from cafe.engine.config import EngineConfig
from cloudcafe.common.tools.md5hash import get_md5_hash

BASE_NAME = "extract_archive"
HTTP_OK = 200


class ExtractArchiveTest(ObjectStorageFixture):
    """
    Tests Swfit expand archive operations:
    """
    @classmethod
    def setUpClass(cls):
        super(ExtractArchiveTest, cls).setUpClass()
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.data_dir = EngineConfig().data_directory
        cls.no_compression = None
        cls.storage_url = cls.client.storage_url
        cls.bad_data = "X" * 1000
        cls.archive_paths = {}
        cls.obj_names = []
        cls.obj_names_with_slashes = []
        cls.obj_names_without_slashes = []

        cls.num_archive_files = 20
        for num in range(cls.num_archive_files):
            if num < 10:
                cls.obj_names_with_slashes.append(
                    "{0}_test{1}/{0}_obj_{1}".format(
                        BASE_NAME,
                        num))
            else:
                cls.obj_names_without_slashes.append("{0}_obj_{1}".format(
                    BASE_NAME,
                    num))

        cls.obj_names = \
            cls.obj_names_with_slashes + cls.obj_names_without_slashes

        tar_archive = cls.client.create_archive(cls.obj_names, None)
        cls.archive_paths["tar"] = tar_archive

        gz_archive = cls.client.create_archive(cls.obj_names, "gz")
        cls.archive_paths["tar.gz"] = gz_archive

        bz2_archive = cls.client.create_archive(cls.obj_names, "bz2")
        cls.archive_paths["tar.bz2"] = bz2_archive

    @classmethod
    def tearDownClass(cls):
        super(ExtractArchiveTest, cls).setUpClass()
        for key in cls.archive_paths.keys():
            os.remove(cls.archive_paths[key])

    def read_archive_data(self, archive_path):
        archive_data = None

        archive_file = open(archive_path, 'r')
        archive_data = archive_file.read()
        archive_file.close()

        return archive_data

    def get_members(self, keys, response_content):
        members = []
        content = None

        try:
            content = json.loads(response_content)
        except ValueError, error:
            self.fixture_log.exception(error)

        for current in content:
            for key in keys:
                if key in current.keys():
                    members.append(current[key])
                else:
                    continue

        return members

    @ObjectStorageFixture.required_features(['bulk'])
    def test_extract_tar_archive_to_existing_container(self):
        """
        Scenario: upload a tar archive with the extract-archive query string
        parameter

        Precondition: Container exists

        Expected Results: tar archive is extracted to objects in an
        existing container
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        data = self.read_archive_data(self.archive_paths['tar'])
        params = {'extract-archive': 'tar'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            headers=headers,
            params=params)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "extract tar archive expected successful status code: {0}"
            " received: {1}".format(expected, received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = self.num_archive_files
        received = int(content.get("Number Files Created"))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '201 Created'
        received = content.get('Response Status')
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(content.get('Errors'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                content.get('Errors')))

        # check the actual number of objects and object names
        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = self.num_archive_files
        received = len(resp_obj_names)
        self.assertEqual(
            expected,
            received,
            msg="container list expected: {0} extracted objects."
            " received: {1} extracted objects".format(expected, received))

        # check that all the objects where extracted to the existing container
        self.assertEqual(sorted(self.obj_names), sorted(resp_obj_names))

        # check that the content of the obj is correct
        # the content should be the md5hash of the objects name
        for name in resp_obj_names:
            response = self.client.get_object(
                container_name,
                name)

            expected = get_md5_hash(name)
            received = response.content
            self.assertEqual(
                expected,
                received,
                msg="obj content expected: {0} received: {1}".format(
                    expected,
                    received))

    @ObjectStorageFixture.required_features(['bulk'])
    def test_extract_tar_gz_archive_to_existing_container(self):
        """
        Scenario: upload a tar.gz archive with the extract-archive query string
        parameter

        Precondition: Container exists

        Expected Results: tar.gz archive is extracted to objects in an
        existing container
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        data = self.read_archive_data(self.archive_paths['tar.gz'])
        params = {'extract-archive': 'tar.gz'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = self.num_archive_files
        received = int(content.get("Number Files Created"))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '201 Created'
        received = content.get('Response Status')
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(content.get('Errors'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                content.get('Errors')))

        # check the actual number of objects and object names
        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = self.num_archive_files
        received = len(resp_obj_names)
        self.assertEqual(
            expected,
            received,
            msg="container list expected: {0} extracted objects."
            " received: {1} extracted objects".format(expected, received))

        # check that all the objects where extracted to the existing container
        self.assertEqual(sorted(self.obj_names), sorted(resp_obj_names))

        # check that the content of the obj is correct
        # the content should be the md5hash of the objects name
        for name in resp_obj_names:
            response = self.client.get_object(
                container_name,
                name)

            expected = get_md5_hash(name)
            received = response.content
            self.assertEqual(
                expected,
                received,
                msg="obj content expected: {0} received: {1}".format(
                    expected,
                    received))

    @ObjectStorageFixture.required_features(['bulk'])
    def test_extract_tar_bz2_archive_to_existing_container(self):
        """
        Scenario: upload a tar.bz2 archive with the extract-archive query
        string parameter

        Precondition: Container exists

        Expected Results: tar archive is extracted to objects in an
        existing container
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        data = self.read_archive_data(self.archive_paths['tar.bz2'])
        params = {'extract-archive': 'tar.bz2'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = self.num_archive_files
        received = int(content.get("Number Files Created"))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '201 Created'
        received = content.get('Response Status')
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(content.get('Errors'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                content.get('Errors')))

        # check the actual number of objects and object names
        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = self.num_archive_files
        received = len(resp_obj_names)
        self.assertEqual(
            expected,
            received,
            msg="container list expected: {0} extracted objects."
            " received: {1} extracted objects".format(expected, received))

        # check that all the objects where extracted to the existing container
        self.assertEqual(sorted(self.obj_names), sorted(resp_obj_names))

        # check that the content of the obj is correct
        # the content should be the md5hash of the objects name
        for name in resp_obj_names:
            response = self.client.get_object(
                container_name,
                name)

            expected = get_md5_hash(name)
            received = response.content
            self.assertEqual(
                expected,
                received,
                msg="obj content expected: {0} received: {1}".format(
                    expected,
                    received))

    @ObjectStorageFixture.required_features(['bulk'])
    def test_extract_tar_archive_without_existing_container(self):
        """
        Scenario: upload a tar archive with the extract-archive query string
        parameter

        Precondition: Container does not exist

        Expected Results: tar archive is object names with slashes are
        extracted to objects. names without slashes are ignored
        """
        data = self.read_archive_data(self.archive_paths['tar'])
        params = {'extract-archive': 'tar'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            self.storage_url,
            data=data,
            headers=headers,
            params=params)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "extract tar archive expected successful status code: {0}"
            " received: {1}".format(expected, received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = len(self.obj_names_with_slashes)
        received = int(content.get("Number Files Created"))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '201 Created'
        received = content.get('Response Status')
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(content.get('Errors'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                content.get('Errors')))

        # check the actual number of objects and object names
        params = {'format': 'json',
                  'marker': BASE_NAME,
                  'limit': str(self.num_archive_files)}
        response = self.client.list_containers(params=params)

        resp_container_names = self.get_members(["name"], response.content)

        # names without slashes are ignored
        for name in self.obj_names_without_slashes:
            self.assertNotIn(name, resp_container_names)

        #container names to be cleaned up
        containers = []

        # names with slashes should create containers with objects in them
        for name in self.obj_names_with_slashes:
            """
            an archive names foo/bar will create a container named foo
            with an object named bar in it.
            """
            container_name = name.split('/')[0]
            obj_name = name.split('/')[1]

            containers.append(container_name)

            # check to see if the expected container name is in the container
            # list response
            self.assertIn(container_name, resp_container_names)

            # check to see if the expected number of objects and obj name are
            # in the obj list response
            params = {'format': 'json'}
            response = self.client.list_objects(container_name, params=params)

            resp_obj_names = self.get_members(["name"], response.content)

            expected = 1
            received = len(resp_obj_names)
            self.assertEqual(
                expected,
                received,
                msg="container list expected: {0} extracted objects."
                " received: {1} extracted objects".format(expected, received))

            self.assertIn(obj_name, resp_obj_names)

            # the content of the obj should be the md5 sum of the obj name
            response = self.client.get_object(
                container_name,
                obj_name)

            expected = get_md5_hash(name)
            received = response.content
            self.assertEqual(
                expected,
                received,
                msg="obj content expected: {0} received: {1}".format(
                    expected,
                    received))

        self.addCleanup(
            self.client.force_delete_containers,
            containers)

    @ObjectStorageFixture.required_features(['bulk'])
    def test_extract_tar_gz_archive_without_existing_container(self):
        """
        Scenario: upload a tar.gz archive with the extract-archive query string
        parameter

        Precondition: Container does not exist

        Expected Results: tar.gz archive is object names with slashes are
        extracted to objects. names without slashes are ignored
        """
        data = self.read_archive_data(self.archive_paths['tar.gz'])
        params = {'extract-archive': 'tar.gz'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            self.storage_url,
            data=data,
            headers=headers,
            params=params)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "extract tar archive expected successful status code: {0}"
            " received: {1}".format(expected, received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = len(self.obj_names_with_slashes)
        received = int(content.get("Number Files Created"))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '201 Created'
        received = content.get('Response Status')
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(content.get('Errors'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                content.get('Errors')))

        # check the actual number of objects and object names
        params = {'format': 'json',
                  'marker': BASE_NAME,
                  'limit': str(self.num_archive_files)}
        response = self.client.list_containers(params=params)

        resp_container_names = self.get_members(["name"], response.content)

        # names without slashes are ignored
        for name in self.obj_names_without_slashes:
            self.assertNotIn(name, resp_container_names)

        #container names to be cleaned up
        containers = []

        # names with slashes should create containers with objects in them
        for name in self.obj_names_with_slashes:
            """
            an archive names foo/bar will create a container named foo
            with an object named bar in it.
            """
            container_name = name.split('/')[0]
            obj_name = name.split('/')[1]

            containers.append(container_name)

            # check to see if the expected container name is in the container
            # list response
            self.assertIn(container_name, resp_container_names)

            # check to see if the expected number of objects and obj name are
            # in the obj list response
            params = {'format': 'json'}
            response = self.client.list_objects(container_name, params=params)

            resp_obj_names = self.get_members(["name"], response.content)

            expected = 1
            received = len(resp_obj_names)
            self.assertEqual(
                expected,
                received,
                msg="container list expected: {0} extracted objects."
                " received: {1} extracted objects".format(expected, received))

            self.assertIn(obj_name, resp_obj_names)

            # the content of the obj should be the md5 sum of the obj name
            response = self.client.get_object(
                container_name,
                obj_name)

            expected = get_md5_hash(name)
            received = response.content
            self.assertEqual(
                expected,
                received,
                msg="obj content expected: {0} received: {1}".format(
                    expected,
                    received))

        self.addCleanup(
            self.client.force_delete_containers,
            containers)

    @ObjectStorageFixture.required_features(['bulk'])
    def test_extract_tar_bz2_archive_without_existing_container(self):
        """
        Scenario: upload a tar.bz2 archive with the extract-archive query
        string parameter

        Precondition: Container does not exist

        Expected Results: tar.bz2 archive is object names with slashes are
        extracted to objects. names without slashes are ignored
        """
        data = self.read_archive_data(self.archive_paths['tar.bz2'])
        params = {'extract-archive': 'tar.bz2'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            self.storage_url,
            data=data,
            headers=headers,
            params=params)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "extract tar archive expected successful status code: {0}"
            " received: {1}".format(expected, received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = len(self.obj_names_with_slashes)
        received = int(content.get("Number Files Created"))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '201 Created'
        received = content.get('Response Status')
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(content.get('Errors'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                content.get('Errors')))

        # check the actual number of objects and object names
        params = {'format': 'json',
                  'marker': BASE_NAME,
                  'limit': str(self.num_archive_files)}
        response = self.client.list_containers(params=params)

        resp_container_names = self.get_members(["name"], response.content)

        # names without slashes are ignored
        for name in self.obj_names_without_slashes:
            self.assertNotIn(name, resp_container_names)

        #container names to be cleaned up
        containers = []

        # names with slashes should create containers with objects in them
        for name in self.obj_names_with_slashes:
            """
            an archive names foo/bar will create a container named foo
            with an object named bar in it.
            """
            container_name = name.split('/')[0]
            obj_name = name.split('/')[1]

            containers.append(container_name)

            # check to see if the expected container name is in the container
            # list response
            self.assertIn(container_name, resp_container_names)

            # check to see if the expected number of objects and obj name are
            # in the obj list response
            params = {'format': 'json'}
            response = self.client.list_objects(container_name, params=params)

            resp_obj_names = self.get_members(["name"], response.content)

            expected = 1
            received = len(resp_obj_names)
            self.assertEqual(
                expected,
                received,
                msg="container list expected: {0} extracted objects."
                " received: {1} extracted objects".format(expected, received))

            self.assertIn(obj_name, resp_obj_names)

            # the content of the obj should be the md5 sum of the obj name
            response = self.client.get_object(
                container_name,
                obj_name)

            expected = get_md5_hash(name)
            received = response.content
            self.assertEqual(
                expected,
                received,
                msg="obj content expected: {0} received: {1}".format(
                    expected,
                    received))

        self.addCleanup(
            self.client.force_delete_containers,
            containers)

    @ObjectStorageFixture.required_features(['bulk'])
    def test_object_creation_with_tar_archive(self):
        """
        Scenario: tar file is uploaded without the extract-archive query
        string parameter.

        Expected Results: contents of the archive are not expanded into objects
        """
        container_name = '{0}_container_{1}'.format(
            'bulk_tar',
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        object_data = self.read_archive_data(self.archive_paths['tar'])
        headers = {'Content-Length': str(len(object_data))}
        obj_name = "{0}_{1}".format(BASE_NAME, self.default_obj_name)
        response = self.client.create_object(
            container_name,
            obj_name,
            data=object_data,
            headers=headers)

        expected = 201
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "object creation with tar archive expected successful status"
            " code: {0} received: {1}".format(expected, received))

        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = 1
        received = len(resp_obj_names)
        self.assertEqual(
            expected,
            received,
            msg="container list expected: {0} objects."
            " received: {1} objects".format(expected, received))

        self.assertIn(obj_name, resp_obj_names)

        response = self.client.get_object(
            container_name,
            obj_name)

        self.assertGreater(response.headers.get('content-length'), 0)

    @ObjectStorageFixture.required_features(['bulk'])
    def test_object_creation_with_tar_gz_archive(self):
        """
        Scenario: tar.gz file is uploaded without the extract-archive query
        string parameter.

        Expected Results: contents of the archive are not expanded into objects
        """
        container_name = '{0}_container_{1}'.format(
            'bulk_tar_gz',
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        object_data = self.read_archive_data(self.archive_paths['tar.gz'])
        headers = {'Content-Length': str(len(object_data))}
        obj_name = "{0}_{1}".format(BASE_NAME, self.default_obj_name)
        response = self.client.create_object(
            container_name,
            obj_name,
            data=object_data,
            headers=headers)

        expected = 201
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "object creation with tar archive expected successful status"
            " code: {0} received: {1}".format(expected, received))

        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = 1
        received = len(resp_obj_names)
        self.assertEqual(
            expected,
            received,
            msg="container list expected: {0} objects."
            " received: {1} objects".format(expected, received))

        self.assertIn(obj_name, resp_obj_names)

        response = self.client.get_object(
            container_name,
            obj_name)

        self.assertGreater(response.headers.get('content-length'), 0)

    @ObjectStorageFixture.required_features(['bulk'])
    def test_object_creation_with_tar_bz2_archive(self):
        """
        Scenario: tar.bz2 file is uploaded without the extract-archive query
        string parameter.

        Expected Results: contents of the archive are not expanded into objects
        """
        container_name = '{0}_container_{1}'.format(
            'bulk_tar_bz2',
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        object_data = self.read_archive_data(self.archive_paths['tar.bz2'])
        headers = {'Content-Length': str(len(object_data))}
        obj_name = "{0}_{1}".format(BASE_NAME, self.default_obj_name)
        response = self.client.create_object(
            container_name,
            obj_name,
            data=object_data,
            headers=headers)

        expected = 201
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "object creation with tar archive expected successful status"
            " code: {0} received: {1}".format(expected, received))

        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = 1
        received = len(resp_obj_names)
        self.assertEqual(
            expected,
            received,
            msg="container list expected: {0} objects."
            " received: {1} objects".format(expected, received))

        self.assertIn(obj_name, resp_obj_names)

        response = self.client.get_object(
            container_name,
            obj_name)

        self.assertGreater(response.headers.get('content-length'), 0)
