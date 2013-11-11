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
import os
import json

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import randomstring as randstring
from cafe.engine.config import EngineConfig

BASE_NAME = "extract_archive"
HTTP_OK = 200


class ExtractArchiveFormatParameterTest(ObjectStorageFixture):
    """
    Tests Swfit expand archive operations:
    """
    @classmethod
    def setUpClass(cls):
        super(ExtractArchiveFormatParameterTest, cls).setUpClass()
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.data_dir = EngineConfig().data_directory
        cls.no_compression = None
        cls.storage_url = cls.client.storage_url
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
        super(ExtractArchiveFormatParameterTest, cls).setUpClass()
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

    def test_failure_reported_with_tar_archive_and_tar_gz_identifier(self):
        """
        Scenario: archive file is uploaded with incorrect extract-archive
        format identifier

        Expected Results: Errors are reported. Objects are not created
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
        params = {'extract-archive': 'tar.gz'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "tar archive with data format tar.gz extraction expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        received = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0} received"
            "{1}".format(expected, received))

        expected = '400 Bad Request'
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

        expected = 'Invalid Tar File: not a gzip file'
        received = content.get('Response Body')
        self.assertIn(
            expected,
            received,
            msg="response body 'Response Body' expected None received"
            " {0}".format(content.get('Response Body')))

    def test_failure_reported_with_tar_archive_and_tar_bz2_identifier(self):
        """
        Scenario: archive file is uploaded with incorrect extract-archive
        format identifier

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        data = self.read_archive_data(self.archive_paths['tar'])
        params = {'extract-archive': 'tar.bz2'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "tar archive with data format tar.bz2 extraction expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        received = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0} received"
            "{1}".format(expected, received))

        expected = '400 Bad Request'
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

        expected = 'Invalid Tar File: invalid compressed data'
        received = content.get('Response Body')
        self.assertIn(
            expected,
            received,
            msg="response body 'Response Body' expected None received"
            " {0}".format(content.get('Response Body')))

    def test_failure_reported_with_tar_gz_archive_and_tar_identifier(self):
        """
        Scenario: archive file is uploaded with incorrect extract-archive
        format identifier

        Expected Results: Errors are reported. Objects are not created
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
        params = {'extract-archive': 'tar'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "tar.gz archive with data format tar extraction expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        received = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0} received"
            "{1}".format(expected, received))

        expected = '400 Bad Request'
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

        expected = 'Invalid Tar File: invalid header'
        received = content.get('Response Body')
        self.assertIn(
            expected,
            received,
            msg="response body 'Response Body' expected None received"
            " {0}".format(content.get('Response Body')))

    def test_failure_reported_with_tar_gz_archive_and_tar_bz2_identifier(self):
        """
        Scenario: archive file is uploaded with incorrect extract-archive
        format identifier

        Expected Results: Errors are reported. Objects are not created
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
        params = {'extract-archive': 'tar.bz2'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "tar.gz archive with data format tar.bz2 extraction expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        received = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0} received"
            "{1}".format(expected, received))

        expected = '400 Bad Request'
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

        expected = 'Invalid Tar File: invalid compressed data'
        received = content.get('Response Body')
        self.assertIn(
            expected,
            received,
            msg="response body 'Response Body' expected None received"
            " {0}".format(content.get('Response Body')))

    def test_failure_reported_with_tar_bz2_archive_and_tar_identifier(self):
        """
        Scenario: archive file is uploaded with incorrect extract-archive
        format identifier

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        data = self.read_archive_data(self.archive_paths['tar.bz2'])
        params = {'extract-archive': 'tar'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "tar.bz2 archive with data format tar extraction expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        received = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0} received"
            "{1}".format(expected, received))

        expected = '400 Bad Request'
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

        expected = 'Invalid Tar File: invalid header'
        received = content.get('Response Body')
        self.assertIn(
            expected,
            received,
            msg="response body 'Response Body' expected None received"
            " {0}".format(content.get('Response Body')))

    def test_failure_reported_with_tar_bz2_archive_and_tar_gz_identifier(self):
        """
        Scenario: archive file is uploaded with incorrect extract-archive
        format identifier

        Expected Results: Errors are reported. Objects are not created
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
        params = {'extract-archive': 'tar.gz'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "tar.bz2 archive with data format tar.gz extraction expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        received = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0} received"
            " {1}".format(expected, received))

        expected = '400 Bad Request'
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

        expected = 'Invalid Tar File: not a gzip file'
        received = content.get('Response Body')
        self.assertIn(
            expected,
            received,
            msg="response body 'Response Body' expected None received"
            " {0}".format(content.get('Response Body')))
