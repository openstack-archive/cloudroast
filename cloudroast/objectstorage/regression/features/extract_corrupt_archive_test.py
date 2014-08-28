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

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import randomstring as randstring
from cafe.engine.config import EngineConfig

BASE_NAME = "extract_corrupt_archive"
HTTP_OK = 200
TAR_MODE_HEADER_OFFSET = 100
TAR_MODE_HEADER_END = 108
TAR_CHKSUM_HEADER_OFFSET = 148
TAR_CHKSUM_HEADER_END = 156
TAR_TYPE_FLAG_HEADER_OFFSET = 156
TAR_TYPE_FLAG_HEADER_END = 157
TAR_GZ_ID1_HEADER = 0
TAR_GZ_ID2_HEADER = 1
TAR_GZ_CM_HEADER = 2
TAR_GZ_FLAG_HEADER = 3
BZ2_MAGIC_HEADER_OFFSET = 0
BZ2_MAGIC_HEADER_END = 2
BZ2_VERSION_HEADER = 2
BZ2_BLOCKSIZE_HEADER = 3


class ExtractCorruptArchiveTest(ObjectStorageFixture):
    """
    Tests Swfit expand archive operations
    """
    @classmethod
    def setUpClass(cls):
        super(ExtractCorruptArchiveTest, cls).setUpClass()
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
        super(ExtractCorruptArchiveTest, cls).setUpClass()
        for key in cls.archive_paths.keys():
            os.remove(cls.archive_paths[key])

    def read_archive_data(self, archive_path):
        archive_data = None

        archive_file = open(archive_path, 'r')
        archive_data = archive_file.read()
        archive_file.close()

        return archive_data

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_archive_bad_checksum(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded.
                  Checksum is overwritten with Null Bytes.

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if (i >= TAR_CHKSUM_HEADER_OFFSET and i < TAR_CHKSUM_HEADER_END):
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: bad checksum'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_archive_bad_type_flag(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded.
                  type flag is overwritten with Null Bytes.

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if (i >= TAR_TYPE_FLAG_HEADER_OFFSET and
                    i < TAR_TYPE_FLAG_HEADER_END):
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: bad checksum'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_archive_bad_mode(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded.
                  mode is overwritten with Null Bytes.

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if (i >= TAR_MODE_HEADER_OFFSET and i < TAR_MODE_HEADER_END):
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: bad checksum'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_gz_archive_bad_ID1(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded
                  flag is overwritten with Null Bytes.

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar.gz"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if i == TAR_GZ_ID1_HEADER:
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar.gz expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: not a gzip file'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_gz_archive_bad_ID2(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded
                  flag is overwritten with Null Bytes.

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar.gz"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if i == TAR_GZ_ID2_HEADER:
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar.gz expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: not a gzip file'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_gz_archive_bad_CM(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded
                  compression mode (CM) is overwritten with Null Bytes.

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar.gz"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if i == TAR_GZ_CM_HEADER:
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar.gz expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: unsupported compression method'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_gz_archive_bad_FLAG(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded
                  flag is overwritten with Null Bytes.

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar.gz"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if i == TAR_GZ_FLAG_HEADER:
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar.gz expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = ('Error -3 while decompressing:'
                    ' invalid distance too far back')
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_bz2_archive_bad_signature(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded
                  signature/magic number is overwritten with null bytes

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar.bz2"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if (i >= BZ2_MAGIC_HEADER_OFFSET and i < BZ2_MAGIC_HEADER_END):
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar.bz2 expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: invalid compressed data'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_bz2_archive_bad_version(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded
                  version is overwritten with null bytes

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar.bz2"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if i == BZ2_VERSION_HEADER:
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar.bz2 expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: invalid compressed data'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))

    @ObjectStorageFixture.required_features('bulk_upload')
    def test_failure_reported_with_corrupt_tar_bz2_archive_bad_blocksize(self):
        """
        Scenario: Verify behavior when a corrupt archive file is uploaded
                  blocksize is overwritten with null bytes

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        archive_format = "tar.bz2"

        temp_data = self.read_archive_data(self.archive_paths[archive_format])

        enumerated_data = enumerate(temp_data)

        temp = []

        for i, char in enumerated_data:
            if i == BZ2_BLOCKSIZE_HEADER:
                temp.append("\x00")
            else:
                temp.append(char)

        data = ''.join(temp)

        headers = {'Accept': 'application/json'}

        response = self.client.create_archive_object(
            data,
            archive_format,
            upload_path=container_name,
            headers=headers)

        expected = HTTP_OK
        received = response.status_code
        self.assertEqual(
            expected,
            received,
            "upload corrupted tar.bz2 expected"
            " successful status code: {0} received: {1}".format(
                expected,
                received))

        expected = 0
        received = int(response.entity.num_files_created)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Number Files Created' expected: {0}"
            " received {1}".format(expected, received))

        expected = '400 Bad Request'
        received = response.entity.status
        self.assertEqual(
            expected,
            received,
            msg="response body 'Response Status' expected: {0}"
            " received {1}".format(expected, received))

        expected = 0
        received = len(response.entity.errors)
        self.assertEqual(
            expected,
            received,
            msg="response body 'Errors' expected None received {0}".format(
                response.entity.errors))

        expected = 'Invalid Tar File: invalid compressed data'
        received = response.entity.body
        self.assertIn(
            expected,
            received,
            msg=("response body 'Response Body' expected '{0}'"
                 " received {1}").format(expected, response.entity.body))
