"""
Copyright 2015 Rackspace

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
from hashlib import md5

from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.objectstorage.generators import (
    ObjectDatasetList, CONTENT_TYPES)

CONTAINER_DESCRIPTOR = 'object_smoke_test'
STATUS_CODE_MSG = ('{method} expected status code {expected}'
                   ' received status code {received}')


@DataDrivenFixture
class ObjectSmokeTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ObjectSmokeTest, cls).setUpClass()
        cls.default_obj_name = Constants.VALID_OBJECT_NAME

    @staticmethod
    def generate_chunk_data():
        for i in range(10):
            yield "Test chunk %s\r\n" % i

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_retrieval_with_valid_object_name(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

        response = self.client.get_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList(exclude=['dlo', 'slo']))
    def ddtest_object_retrieval_with_if_match(
            self, object_type, generate_object):
        """
        Bug filed for dlo/slo support of If-match Header:
        https://bugs.launchpad.net/swift/+bug/1279076
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        obj_info = generate_object(container_name, object_name)

        headers = {'If-Match': obj_info.get('etag')}

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

    @data_driven_test(ObjectDatasetList(exclude=['dlo', 'slo']))
    def ddtest_object_retrieval_with_if_none_match(
            self, object_type, generate_object):
        """
        Bug filed for dlo/slo support of If-match Header:
        https://bugs.launchpad.net/swift/+bug/1279076
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_info = generate_object(container_name, object_name)

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

        headers = {'If-None-Match': object_info.get('etag')}

        response = self.client.get_object(
            container_name,
            self.default_obj_name,
            headers=headers)

        method = 'object should be flagged as not modified'
        expected = 304
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_retrieval_with_if_modified_since(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_not_modified_with_if_modified_since(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_retrieval_with_if_unmodified_since(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_retrieval_fails_with_if_unmodified_since(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_partial_object_retrieval_with_start_range(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_partial_object_retrieval_with_end_range(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_partial_object_retrieval_with_range(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_partial_object_retrieval_with_complete_range(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_valid_object_name(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_info = generate_object(container_name, object_name)

        response = object_info.get('response')
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

        response_md5 = md5(response.content).hexdigest()
        self.assertEqual(
            object_info.get('md5'),
            response_md5,
            msg='should return identical object')

    @data_driven_test(ObjectDatasetList(exclude=['dlo', 'slo']))
    def ddtest_object_update_with_valid_object_name(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

        updated_object_data = 'Updated test file data'
        updated_content_length = str(len(updated_object_data))
        headers = {'Content-Length': updated_content_length,
                   'Content-Type': CONTENT_TYPES.get('text')}
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_etag(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_info = generate_object(container_name, object_name)

        response = object_info.get('response')
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

        response = self.client.get_object(
            container_name,
            self.default_obj_name)
        self.assertIn(
            'etag',
            response.headers,
            msg="Etag header was set")

        if object_type == 'standard':
            expected = object_info.get('etag')
        else:
            expected = '"{0}"'.format(object_info.get('etag'))
        received = response.headers.get('etag')

        self.assertEqual(
            expected,
            received,
            msg='object created with Etag header'
                ' value expected: {0} received: {1}'.format(
                    expected,
                    received))

    @data_driven_test(ObjectDatasetList(exclude=['dlo', 'slo']))
    def test_object_creation_with_uppercase_etag(self):

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_data = "valid_data"
        data_md5 = md5(object_data).hexdigest()
        upper_etag = data_md5.upper()

        headers = {"ETag": upper_etag}
        create_response = self.client.create_object(container_name,
                                                    object_name,
                                                    data=object_data,
                                                    headers=headers)

        method = 'object creation with uppercase etag header'
        expected = 201
        received = create_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(
            container_name,
            self.default_obj_name)
        self.assertIn(
            'etag',
            object_response.headers,
            msg="Etag header was set")

        expected = data_md5
        received = object_response.headers.get('etag')

        self.assertEqual(
            expected,
            received,
            msg='object created with Etag header'
                ' value expected: {0} received: {1}'.format(
                    expected,
                    received))

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_creation_with_access_control_allow_credentials(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {'Access-Control-Allow-Credentials': 'true'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_creation_with_access_control_allow_methods(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_creation_with_access_control_allow_origin(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {
            'Access-Control-Allow-Origin': 'http://example.com'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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
            container_name, self.default_obj_name)

        self.assertIn(
            'Access-Control-Allow-Origin',
            response.headers,
            msg="Access-Control-Allow-Origin header was set")

        expected = 'http://example.com'
        received = response.headers.get('Access-Control-Allow-Origin')

        self.assertEqual(
            expected,
            received,
            msg='object created with Access-Control-Allow-Origin header'
                ' value expected: {0} recieved: {1}'.format(
                    expected,
                    received))

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_creation_with_access_control_expose_headers(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {'Access-Control-Expose-Headers': 'X-Foo-Header'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_creation_with_access_controle_max_age(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {'Access-Control-Max-Age': '5'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_creation_with_access_control_request_headers(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {'Access-Control-Request-Headers': 'x-requested-with'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_creation_with_access_control_request_method(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {'Access-Control-Request-Method': 'GET'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object-cors')
    def ddtest_object_retrieval_with_origin(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        headers = {'access-control-allow-origin': 'http://example.com',
                   'access-control-expose-headers': 'X-Trans-Id'}
        generate_object(container_name, object_name, headers=headers)

        headers = {'Origin': 'http://example.com'}
        response = self.client.get_object_metadata(
            container_name, object_name, headers=headers)

        self.assertIn(
            'access-control-expose-headers',
            response.headers,
            msg="access-control-expose-headers header should be set")

        self.assertIn(
            'access-control-allow-origin',
            response.headers,
            msg="access-control-allow-origin header should be set")

        expected = 'http://example.com'
        received = response.headers.get('access-control-allow-origin')

        self.assertEqual(
            expected,
            received,
            msg='access-control-allow-origin header should reflect origin'
                ' expected: {0} recieved: {1}'.format(expected, received))

    @data_driven_test(ObjectDatasetList(exclude=['dlo', 'slo']))
    def ddtest_object_creation_with_file_compression(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name

        def object_data_op(data, extra_data):
            data = zlib.compress(data)
            return (data, extra_data)

        object_headers = {'Content-Encoding': 'gzip'}
        object_info = generate_object(container_name, object_name,
                                      data_op=object_data_op,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_content_disposition(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {
            'Content-Disposition': 'attachment; filename=testdata.txt'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_x_delete_at(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name

        start_time = calendar.timegm(time.gmtime())
        future_time = str(int(start_time + 60))
        object_headers = {'X-Delete-At': future_time}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_creation_with_delete_after(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        object_headers = {'X-Delete-After': '60'}
        object_info = generate_object(container_name, object_name,
                                      headers=object_headers)

        response = object_info.get('response')
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

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('object_versioning')
    def ddtest_versioned_container_creation_with_valid_data(
            self, object_type, generate_object):

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_history_container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        headers = {'X-Versions-Location': object_history_container_name}
        self.client.set_container_metadata(container_name, headers=headers)

        # list objects in non-current container
        response = self.client.list_objects(
            object_history_container_name)

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

        # Create an object (version 1)
        object_name = self.default_obj_name
        ver1_info = generate_object(container_name, object_name)

        response = ver1_info.get('response')
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

        # Update an object (version 2)
        object_name = self.default_obj_name
        ver2_info = generate_object(container_name, object_name)

        response = ver2_info.get('response')
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

        response = self.client.list_objects(object_history_container_name)
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_put_copy_object(self, object_type, generate_object):
        src_container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        dest_container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        src_object_name = '{0}_source'.format(self.default_obj_name)
        generate_object(src_container_name, src_object_name)

        dest_obj_name = '{0}_destination'.format(self.default_obj_name)
        source = '/{0}/{1}'.format(src_container_name, src_object_name)
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

    @data_driven_test(ObjectDatasetList())
    def ddtest_copy_object(self, object_type, generate_object):
        src_container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        dest_container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        src_object_name = '{0}_source'.format(self.default_obj_name)
        generate_object(src_container_name, src_object_name)

        dest_object_name = '{0}_destination'.format(self.default_obj_name)
        dest = '/{0}/{1}'.format(dest_container_name, dest_object_name)
        headers = {'Destination': dest}

        response = self.client.copy_object(
            src_container_name,
            src_object_name,
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
            dest_object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_object_deletion_with_valid_object(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

        response = self.client.delete_object(
            container_name,
            object_name)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_obj_metadata_update_with_object_possessing_metadata(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name,
                        headers={'X-Object-Meta-Grok': 'Drok'})
        response = self.client.get_object_metadata(
            container_name, object_name)

        self.assertIn(
            'X-Object-Meta-Grok',
            response.headers,
            msg="object not created with X-Object-Meta-Grok header")

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_obj_metadata_update(self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.default_obj_name
        generate_object(container_name, object_name)

        headers = {'X-Object-Meta-Grok': 'Drok'}
        response = self.client.set_object_metadata(
            container_name, object_name, headers=headers)

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

    @data_driven_test(ObjectDatasetList())
    def ddtest_content_type_not_detected_without_detect_content_type_header(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object1_name = 'object1.txt'
        object1_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        generate_object(container_name, object1_name, headers=object1_headers)

        object2_name = 'object2.txt'
        object2_headers = {'X-Detect-Content-Type': False,
                           'Content-Type': 'application/x-www-form-urlencoded'}
        generate_object(container_name, object2_name, headers=object2_headers)

        response = self.client.get_object(
            container_name, object1_name)

        expected = 'application/x-www-form-urlencoded'
        received = response.headers.get('content-type')

        self.assertEqual(
            expected,
            received,
            msg='object created should have content type: {0}'
                ' recieved: {1}'.format(expected, received))

        response = self.client.get_object(
            container_name, object2_name)

        self.assertEqual(
            expected,
            received,
            msg='object created should have content type: {0}'
                ' recieved: {1}'.format(expected, received))

    @data_driven_test(ObjectDatasetList())
    def ddtest_content_type_detected_with_detect_content_type(
            self, object_type, generate_object):
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object1_name = 'object1.txt'
        object1_headers = {'X-Detect-Content-Type': True,
                           'Content-Type': 'application/x-www-form-urlencoded'}
        generate_object(container_name, object1_name, headers=object1_headers)

        response = self.client.get_object(
            container_name, object1_name)

        expected = 'text/plain'
        received = response.headers.get('content-type')

        self.assertEqual(
            expected,
            received,
            msg='object created should have content type: {0}'
                ' recieved: {1}'.format(expected, received))

        object2_name = 'object2.txt'
        object2_headers = {'X-Detect-Content-Type': True}
        generate_object(container_name, object2_name, headers=object2_headers)

        response = self.client.get_object(
            container_name, object2_name)

        expected = 'text/plain'
        received = response.headers.get('content-type')

        self.assertEqual(
            expected,
            received,
            msg='object created should have content type: {0}'
                ' recieved: {1}'.format(expected, received))

    def test_object_creation_via_chunked_transfer(self):
        """
        Scenario:
            Create an object using chunked transfer encoding.

        Expected Results:
            Return a 201 status code and a single object should
            be created.
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        headers = {"Transfer-Encoding": "chunked"}

        create_response = self.client.create_object(
            container_name,
            self.default_obj_name,
            headers=headers,
            data=self.generate_chunk_data())

        method = 'Object creation via chunked transfer'
        expected = 201
        received = create_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(container_name,
                                                 self.default_obj_name)

        method = 'Object retrieval'
        expected = 200
        received = object_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))
