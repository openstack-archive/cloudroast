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
import zlib

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import md5hash

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
CONTAINER_NAME = 'object_smoke_test'
STATUS_CODE_MSG = ('{method} expected status code {expected}'
    ' received status code {received}')


class ObjectSmokeTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ObjectSmokeTest, cls).setUpClass()

        cls.base_container_name = CONTAINER_NAME
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.default_obj_data = cls.behaviors.VALID_OBJECT_DATA

    def test_object_retrieval_with_valid_object_name(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        response = self.client.get_object(
            container_name,
            self.default_obj_name)

        method = 'object creation with valid object name'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_retrieval_with_if_match(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        etag = md5hash.get_md5_hash(self.default_obj_data)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Etag': etag}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'If-Match': etag}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'object retrieval with if match header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_retrieval_with_if_none_match(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'If-None-Match': 'grok'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'object retrieval with if none match header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_retrieval_with_if_modified_since(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'If-Modified-Since': 'Fri, 17 Aug 2001 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'object retrieval with if modified since header (past date)'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_not_modified_with_if_modified_since(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'If-Modified-Since': 'Fri, 17 Aug 2101 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'object retrieval with if modified since header (future date)'
        expected = 304
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_retrieval_with_if_unmodified_since(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'If-Unmodified-Since': 'Fri, 17 Aug 2101 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'object retrieval with if unmodified since header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_retrieval_fails_with_if_unmodified_since(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'If-Unmodified-Since': 'Fri, 17 Aug 2001 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = ('object retrieval precondition fail with if unmodified'
            ' since header')
        expected = 412
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_partial_object_retrieval_with_start_range(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Range': 'bytes=5-'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'partial object retrieval with start range'
        expected = 206
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_partial_object_retrieval_with_end_range(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Range': 'bytes=-4'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'partial object retrieval with end range'
        expected = 206
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_partial_object_retrieval_with_range(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Range': 'bytes=5-8'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'partial object retrieval with start and end range'
        expected = 206
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_partial_object_retrieval_with_complete_range(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Range': 'bytes=99-0'}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'partial object retrieval with complete range'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_creation_with_valid_object_name(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with valid object name'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object(
            container_name,
            self.default_obj_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_update_with_valid_object_name(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        updated_object_data = 'Updated test file data'

        updated_content_length = str(len(updated_object_data))

        headers = {'Content-Length': updated_content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=updated_object_data)

        method = 'object update with valid object name'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_creation_with_etag(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        etag = md5hash.get_md5_hash(self.default_obj_data)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Etag': etag}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with etag header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Etag',
            response.headers,
            msg="Etag header was set")

        expected = etag
        received = response.headers.get('Etag')

        self.assertEqual(
            expected,
            received,
            msg='object created with Etag header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_dlo_creation(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        segment1_name = '{0}{1}'.format(self.default_obj_name, '.1')
        segment1_data = 'Segment 1'
        segment1_length = str(len(segment1_data))

        headers = {'Content-Length': segment1_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            segment1_name,
            headers=headers,
            data=segment1_data)

        method = 'large object segment 1 creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        segment2_name = '{0}{1}'.format(self.default_obj_name, '.2')
        segment2_data = 'Segment 2'
        segment2_length = str(len(segment2_data))

        headers = {'Content-Length': segment2_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            segment2_name,
            headers=headers,
            data=segment2_data)

        method = 'large object segment 2 creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        large_object_common_prefix = '{0}/{1}'.format(
            container_name, self.default_obj_name)

        headers = {'Content-Length': '0',
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Manifest': large_object_common_prefix}

        self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'manifest creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object(
            container_name,
            self.default_obj_name)

        method = 'assembled large object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_dlo_retrieval_with_range(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        segment1_name = '{0}{1}'.format(self.default_obj_name, '.1')
        segment1_data = 'Segment 1'
        segment1_length = str(len(segment1_data))

        headers = {'Content-Length': segment1_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            segment1_name,
            headers=headers,
            data=segment1_data)

        method = 'large object segment 1 creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        segment2_name = '{0}{1}'.format(self.default_obj_name, '.2')
        segment2_data = 'Segment 2'
        segment2_length = str(len(segment2_data))

        headers = {'Content-Length': segment2_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            segment2_name,
            headers=headers,
            data=segment2_data)

        method = 'large object segment 2 creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        large_object_common_prefix = '{0}/{1}'.format(
            container_name,
            self.default_obj_name)

        headers = {'Content-Length': '0',
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Manifest': large_object_common_prefix}

        self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'manifest creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object(
            container_name,
            self.default_obj_name, headers={'Range': 'bytes=0-10'})

        method = 'dlo retrieval with range header'
        expected = 206
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_creation_with_access_control_allow_credentials(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Credentials': 'true'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Access-Control-Allow-Credentials header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Access-Control-Allow-Credentials',
            response.headers,
            msg="Access-Control-Allow-Credentials header was set")

        expected = 'true'
        received = response.headers.get('Access-Control-Allow-Credentials')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Allow-Credentials header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_object_creation_with_access_control_allow_methods(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Access-Control-Allow-Methods header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Access-Control-Allow-Methods',
            response.headers,
            msg="Access-Control-Allow-Methods header was set")

        expected = 'GET, POST, OPTIONS'
        received = response.headers.get('Access-Control-Allow-Methods')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Allow-Methods header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_object_creation_with_access_control_allow_origin(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Origin': 'http://foobar.org'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Access-Control-Allow-Origin header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Access-Control-Allow-Origin',
            response.headers,
            msg="Access-Control-Allow-Origin header was set")

        expected = 'http://foobar.org'
        received = response.headers.get('Access-Control-Allow-Origin')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Allow-Origin header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_object_creation_with_access_control_expose_headers(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Expose-Headers': 'X-Foo-Header'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Access-Control-Expose-Headers header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Access-Control-Expose-Headers',
            response.headers,
            msg="Access-Control-Expose-Headers header was set")

        expected = 'X-Foo-Header'
        received = response.headers.get('Access-Control-Expose-Headers')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Expose-Headers header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_object_creation_with_access_controle_max_age(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Max-Age': '5'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Access-Control-Max-Age header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Access-Control-Max-Age',
            response.headers,
            msg="Access-Control-Max-Age header was set")

        expected = '5'
        received = response.headers.get('Access-Control-Max-Age')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Max-Age header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_object_creation_with_access_control_request_headers(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Request-Headers': 'x-requested-with'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Access-Control-Request-Headers header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Access-Control-Request-Headers',
            response.headers,
            msg="Access-Control-Request-Headers header was set")

        expected = 'x-requested-with'
        received = response.headers.get('Access-Control-Request-Headers')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Request-Headers header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_object_creation_with_access_control_request_method(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Request-Method': 'GET'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Access-Control-Request-Method header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Access-Control-Request-Method',
            response.headers,
            msg="Access-Control-Request-Method header was set")

        expected = 'GET'
        received = response.headers.get('Access-Control-Request-Method')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Request-Method header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    def test_object_creation_with_origin(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Origin': 'http://foobar.org'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with Origin header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Origin',
            response.headers,
            msg="Origin header was set")

        expected = 'http://foobar.org'
        received = response.headers.get('Origin')

        self.assertEqual(
            expected,
            received,
            msg='object created with Origin header value'
                ' expected: {0} recieved: {1}'.format(expected, received))

    def test_object_creation_with_file_compression(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        temp_object_data = 'Uncompressed test file data'
        compressed_object_data = zlib.compress(temp_object_data)
        compressed_length = str(len(compressed_object_data))
        headers = {'Content-Length': compressed_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Encoding': 'gzip'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=compressed_object_data)

        method = 'object creation with Content-Encoding header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Content-Encoding',
            response.headers,
            msg="Content-Encoding header was set")

        expected = 'gzip'
        received = response.headers.get('Content-Encoding')

        self.assertEqual(
            expected,
            received,
            msg='object created with Content-Encoding header value'
                ' expected: {0} recieved: {1}'.format(expected, received))

    def test_object_creation_with_content_disposition(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Disposition': 'attachment; filename=testdata.txt'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with content disposition header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'Content-Disposition',
            response.headers,
            msg="Content-Disposition header was set")

        expected = 'attachment; filename=testdata.txt'
        received = response.headers.get('Content-Disposition')

        self.assertEqual(
            expected,
            received,
            msg='object created with Content-Disposition header value'
                ' expected: {0} recieved: {1}'.format(expected, received))

    def test_object_creation_with_x_delete_at(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        start_time = calendar.timegm(time.gmtime())
        future_time = str(int(start_time + 60))
        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Delete-At': future_time}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with X-Delete-At header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'X-Delete-At',
            response.headers,
            msg="X-Delete-At header was set")

        expected = future_time
        received = response.headers.get('X-Delete-At')

        self.assertEqual(
            expected,
            received,
            msg='object created with X-Delete-At header value'
                ' expected: {0} recieved: {1}'.format(expected, received))

    def test_object_creation_with_delete_after(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Delete-After': '60'}

        response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        method = 'object creation with X-Delete-After header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'X-Delete-At',
            response.headers,
            msg="X-Delete-At header was set")

    @ObjectStorageFixture.required_features(['object_versioning'])
    def test_versioned_container_creation_with_valid_data(self):
        # Create a container for 'non-current' object storage
        non_current_container_name = (
            self.behaviors.generate_unique_container_name(
                'non_current'))

        self.behaviors.create_container(non_current_container_name)

        # Create a container for 'current' object storage
        current_container_headers = {
            'X-Versions-Location': non_current_container_name}

        current_container_name = (
            self.behaviors.generate_unique_container_name(
                'current'))

        self.behaviors.create_container(
            current_container_name,
            headers=current_container_headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [current_container_name])

        self.addCleanup(
            self.client.force_delete_containers,
            [non_current_container_name])

        # list objects in non-current container
        response = self.client.list_objects(
            non_current_container_name)

        method = 'list on empty versioned container'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        #Create an object (version 1)
        object_data_version1 = 'Version 1'
        version1_length = str(len(object_data_version1))
        headers = {'Content-Length': version1_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            current_container_name,
            self.default_obj_name,
            headers=headers,
            data=object_data_version1)

        method = 'object version one creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        #Update an object (version 2)
        object_data_version2 = 'Version 2'
        version2_length = str(len(object_data_version2))
        headers = {'Content-Length': version2_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            current_container_name,
            self.default_obj_name,
            headers=headers,
            data=object_data_version2)

        method = 'update version one object'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.list_objects(
            non_current_container_name)

        method = 'list on versioned container'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_put_copy_object(self):
        src_container_name = self.behaviors.generate_unique_container_name(
            '{0}_{1}'.format(self.base_container_name, 'src'))

        dest_container_name = self.behaviors.generate_unique_container_name(
            '{0}_{1}'.format(self.base_container_name, 'dst'))

        self.behaviors.create_container(src_container_name)

        self.behaviors.create_container(dest_container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [dest_container_name])

        self.addCleanup(
            self.client.force_delete_containers,
            [src_container_name])

        src_obj_name = '{0}_source'.format(self.default_obj_name)

        dest_obj_name = '{0}_destination'.format(self.default_obj_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            src_container_name,
            src_obj_name,
            headers=headers,
            data=self.default_obj_data)

        source = '/{0}/{1}'.format(src_container_name, src_obj_name)
        hdrs = {'X-Copy-From': source, 'Content-Length': '0'}

        response = self.client.copy_object(
            dest_container_name,
            dest_obj_name,
            headers=hdrs)

        method = 'put copy object'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object(
            dest_container_name,
            dest_obj_name)

        method = 'copied object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_copy_object(self):
        src_container_name = self.behaviors.generate_unique_container_name(
            '{0}_{1}'.format(self.base_container_name, 'src'))

        dest_container_name = self.behaviors.generate_unique_container_name(
            '{0}_{1}'.format(self.base_container_name, 'dst'))

        self.behaviors.create_container(src_container_name)

        self.behaviors.create_container(dest_container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [dest_container_name])

        self.addCleanup(
            self.client.force_delete_containers,
            [src_container_name])

        src_obj_name = '{0}_source'.format(self.default_obj_name)

        dest_obj_name = '{0}_destination'.format(self.default_obj_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            src_container_name,
            src_obj_name,
            headers=headers,
            data=self.default_obj_data)

        dest = '/{0}/{1}'.format(dest_container_name, dest_obj_name)
        headers = {'Destination': dest}

        response = self.client.copy_object(
            src_container_name,
            src_obj_name,
            headers=headers)

        method = 'copy object'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object(
            dest_container_name,
            dest_obj_name)

        method = 'copied object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_object_deletion_with_valid_object(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        response = self.client.delete_object(
            container_name,
            self.default_obj_name)

        method = 'delete object'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object(
            container_name,
            self.default_obj_name)

        method = 'object retrieval'
        expected = 404
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    def test_obj_metadata_update_with_object_possessing_metadata(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Meta-Grok': 'Drok'}

        self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.default_obj_data)

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'X-Object-Meta-Grok',
            response.headers,
            msg="object created with X-Object-Meta-Grok header")

        expected = 'Drok'
        received = response.headers.get('X-Object-Meta-Grok')

        self.assertEqual(
            expected,
            received,
            msg='object created with X-Object-Meta-Grok header value'
                ' expected: {0} recieved: {1}'.format(expected, received))

        headers = {'X-Object-Meta-Foo': 'Bar'}

        response = self.client.set_object_metadata(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'set object metadata'
        expected = 202
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'X-Object-Meta-Foo',
            response.headers,
            msg="object updated with X-Object-Meta-Foo header")

        expected = 'Bar'
        received = response.headers.get('X-Object-Meta-Foo')

        self.assertEqual(
            expected,
            received,
            msg='object X-Object-Meta-Foo header value expected: {0}'
                ' recieved: {1}'.format(expected, received))

    def test_obj_metadata_update(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.behaviors.create_object(
            container_name,
            self.default_obj_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        headers = {'X-Object-Meta-Grok': 'Drok'}

        response = self.client.set_object_metadata(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'set object metadata X-Object-Meta-Grok: Drok'
        expected = 202
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            self.default_obj_name)

        self.assertIn(
            'X-Object-Meta-Grok',
            response.headers,
            msg="object updated with X-Object-Meta-Grok header")

        expected = 'Drok'
        received = response.headers.get('X-Object-Meta-Grok')

        self.assertEqual(
            expected,
            received,
            msg='object X-Object-Meta-Grok header value expected: {0}'
                ' recieved: {1}'.format(expected, received))

    def test_content_type_not_detected_without_detect_content_type_header(
            self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        obj1_name = 'object1.txt'

        obj1_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        self.behaviors.create_object(
            container_name,
            obj1_name,
            data=self.default_obj_data,
            headers=obj1_headers)

        obj2_name = 'object2.txt'

        obj2_headers = {'X-Detect-Content-Type': False,
                        'Content-Type': 'application/x-www-form-urlencoded'}

        self.behaviors.create_object(
            container_name,
            obj2_name,
            data=self.default_obj_data,
            headers=obj2_headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        response = self.client.get_object(
            container_name,
            obj1_name)

        expected = 'application/x-www-form-urlencoded'
        received = response.headers.get('content-type')

        self.assertEqual(
            expected,
            received,
            msg='object created should have content type: {0}'
                ' recieved: {1}'.format(expected, received))

        response = self.client.get_object(
            container_name,
            obj2_name)

        self.assertEqual(
            expected,
            received,
            msg='object created should have content type: {0}'
                ' recieved: {1}'.format(expected, received))

    def test_content_type_detected_with_detect_content_type(self):
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        object1_name = 'object1.txt'

        headers = {'X-Detect-Content-Type': True,
                   'Content-Type': 'application/x-www-form-urlencoded'}

        self.behaviors.create_object(
            container_name,
            object1_name,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        response = self.client.get_object(
            container_name,
            object1_name)

        expected = 'text/plain'
        received = response.headers.get('content-type')

        self.assertEqual(
            expected,
            received,
            msg='object created should have content type: {0}'
                ' recieved: {1}'.format(expected, received))
