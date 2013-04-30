import calendar
import time
import zlib

from test_repo.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import md5hash
from cloudcafe.common.tools import randomstring

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
STATUS_CODE_MSG = '{method} expected status code {expected}' \
    ' received status code {received}'


class ObjectSmokeTest(ObjectStorageFixture):
    """4.3.1. Retrieve Object"""
    def test_object_retrieval_with_valid_object_name(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object creation with valid object name'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_retrieval_with_if_match_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        etag = md5hash.get_md5_hash(object_data)

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Etag': etag}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'If-Match': etag}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'object retrieval with if match header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_retrieval_with_if_none_match_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        etag = md5hash.get_md5_hash(object_data)

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Etag': etag}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'If-None-Match': 'grok'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'object retrieval with if none match header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_retrieval_with_if_modified_since_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'If-Modified-Since': 'Fri, 17 Aug 2001 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'object retrieval with if modified since header (past date)'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_not_modified_with_if_modified_since_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'If-Modified-Since': 'Fri, 17 Aug 2101 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'object retrieval with if modified since header (future date)'
        expected = 304
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_retrieval_with_if_unmodified_since_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'If-Unmodified-Since': 'Fri, 17 Aug 2101 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'object retrieval with if unmodified since header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_retrieval_fails_with_if_unmodified_since_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'If-Unmodified-Since': 'Fri, 17 Aug 2001 18:44:42 GMT'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'object retrieval precondition fail with if unmodified' \
            ' since header'
        expected = 412
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_partial_object_retrieval_with_start_range(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Range': 'bytes=5-'}

        response = self.client.get_object(
            container_name,
            object_name,
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
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Range': 'bytes=-4'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'partial object retrieval with end range'
        expected = 206
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_partial_object_retrieval_with_range(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers,
                        [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Range': 'bytes=5-8'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'partial object retrieval with start and end range'
        expected = 206
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_partial_object_retrieval_with_complete_range(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'Range': 'bytes=99-0'}

        response = self.client.get_object(
            container_name,
            object_name,
            headers=headers)

        method = 'partial object retrieval with complete range'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.2. Create/Update Object"""
    def test_object_creation_with_valid_object_name(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with valid object name'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_update_with_valid_object_name(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        object_data = 'Updated test file data'

        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object update with valid object name'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_etag_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Etag': md5hash.get_md5_hash(object_data)}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with etag header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_metadata(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Meta-Grok': 'Drok'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with metadata'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.2.1. Dynamic Large Object Creation"""
    def test_object_creation_with_dynamic_large_object(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        segment_name = '{0}{1}'.format(object_name, '.1')
        segment_data = 'Segment 1'
        content_length = str(len(segment_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            segment_name,
            headers=headers,
            data=segment_data)

        method = 'large object segment 1 creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        segment_name = '{0}{1}'.format(object_name, '.2')
        segment_data = 'Segment 2'
        content_length = str(len(segment_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            segment_name,
            headers=headers,
            data=segment_data)

        method = 'large object segment 2 creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        large_object_common_prefix = '{0}/{1}'.format(
            container_name, object_name)
        headers = {'Content-Length': '0',
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Manifest': large_object_common_prefix}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers)

        method = 'large object manifest creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'assembled large object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.2.4. Assigning CORS Headers to Requests"""
    def test_object_creation_with_cors_allow_credentials_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Credentials': 'true'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors access control allow' \
            ' credentials header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_cors_access_control_allow_methods(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors access control allow' \
            ' methods header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_cors_allow_origin_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Origin': 'http://foobar.org'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors access control allow' \
            ' origin header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_cors_expose_headers_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Expose-Headers': 'X-Foo-Header'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors expose headers header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_cors_max_age_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Max-Age': '5'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors max age header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_cors_request_headers_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Request-Headers': 'x-requested-with'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors request headers header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_cors_request_method_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Request-Method': 'GET'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors request method header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_cors_origin_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Origin': 'http://foobar.org'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors origin header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.2.5. Enabling File Compression with the Content-Encoding Header"""
    def test_object_retrieval_with_file_compression(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_data = 'Uncompressed test file data'
        compressed_object_data = zlib.compress(object_data)
        content_length = str(len(compressed_object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Encoding': 'gzip'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=compressed_object_data)

        method = 'object creation with cors content encoding header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.2.6. Enabling Browser Bypass with the Content-Disposition Header"""
    def test_object_retrieval_with_browser_bypass(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Disposition': 'attachment; filename=testdata.txt'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with cors content disposition header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """
    4.3.2.7. Expiring Objects with the X-Delete-After and X-Delete-At Headers
    """
    def test_object_creation_with_x_delete_at_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        start_time = calendar.timegm(time.gmtime())
        future_time = str(int(start_time + 60))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Delete-At': future_time}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation x delete at header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_object_creation_with_delete_after_header(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Delete-After': '60'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation x delete after header'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.2.8. Object Versioning"""
    def test_versioned_container_creation_with_valid_data(self):
        #Create a container for 'non-current' object storage
        non_current_version_container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(
            non_current_version_container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [non_current_version_container_name])

        #Create a container for 'current' object storage
        current_version_container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        current_version_container_headers = \
            {'X-Versions-Location': non_current_version_container_name}

        self.client.create_container(
            current_version_container_name,
            headers=current_version_container_headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [current_version_container_name])

        #Create an object (version 1)
        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Version 1'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            current_version_container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object version one creation'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.list_objects(
            non_current_version_container_name)

        method = 'list on empty versioned container'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        #Update an object (version 2)
        object_data = 'Version 2'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            current_version_container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'update version one object'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.list_objects(
            non_current_version_container_name)

        method = 'list on versioned container'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.3. Copy Object"""
    def test_put_copy_object(self):
        src_container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(src_container_name)

        dest_container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(dest_container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [src_container_name, dest_container_name])

        src_obj_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            src_container_name,
            src_obj_name,
            headers=headers,
            data=object_data)

        dest_obj_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())

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
                method=method, expected=expected, received=str(received)))

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
                method=method, expected=expected, received=str(received)))

    def test_copy_object(self):
        src_obj_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))

        src_container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(src_container_name)

        dest_container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(dest_container_name)

        dest_obj_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())

        self.addCleanup(
            self.client.force_delete_containers,
            [src_container_name, dest_container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            src_container_name,
            src_obj_name,
            headers=headers,
            data=object_data)

        dest = '/{0}/{1}'.format(dest_container_name, dest_obj_name)
        hdrs = {'Destination': dest}

        response = self.client.copy_object(
            src_container_name,
            src_obj_name,
            headers=hdrs)

        method = 'copy object'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

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
                method=method, expected=expected, received=str(received)))

    """4.3.4. Delete Object"""
    def test_object_deletion_with_valid_object(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        self.assertEqual(response.status_code, 201, 'should be created')

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
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object(
            container_name,
            object_name)

        method = 'object retrieval'
        expected = 404
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.5. Retrieve Object Metadata"""
    def test_metadata_retrieval_with_newly_created_object(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Meta-Grok': 'Drok'}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        method = 'object creation with x object meta'
        expected = 201
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            object_name)

        method = 'object metadata retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_metadata_retrieval_with_object_possessing_metadata(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        metadata = {'Grok': 'Drok'}

        response = self.client.set_object_metadata(
            container_name,
            object_name,
            metadata)

        method = 'set object metadata'
        expected = 202
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        response = self.client.get_object_metadata(
            container_name,
            object_name)

        method = 'object metadata retrieval'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.3.6. Update Object Metadata"""
    def test_object_update_with_metadata(self):
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randomstring.get_random_string())

        self.client.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        object_name = '{0}_{1}'.format(
            self.base_object_name,
            randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        metadata = {'Foo': 'Bar'}

        response = self.client.set_object_metadata(
            container_name,
            object_name,
            metadata)

        method = 'set object metadata'
        expected = 202
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

        metadata = {'Grok': 'Drok'}

        response = self.client.set_object_metadata(
            container_name,
            object_name,
            metadata)

        method = 'update object metadata'
        expected = 202
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))
