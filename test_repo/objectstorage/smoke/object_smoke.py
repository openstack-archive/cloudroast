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

from test_repo.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import md5hash
from cloudcafe.common.tools import randomstring

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'


class ObjectSmokeTest(ObjectStorageFixture):
    def setup_container(self, base_name, headers=None):
        container_name = '{0}_{1}'.format(
            base_name,
            randomstring.get_random_string())

        self.client.create_container(container_name, headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        return container_name

    def test_object_retrieval_with_valid_object_name(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 200, 'should return object.')

    def test_object_retrieval_with_if_match_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_retrieval_with_if_none_match_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_retrieval_with_if_modified_since_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_not_modified_with_if_modified_since_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            304,
            'should not retrieve object')

    def test_object_retrieval_with_if_unmodified_since_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_precondition_fail_with_if_unmodified_since_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            412,
            'should not retrieve object')

    def test_object_not_modified_with_if_unmodified_since_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_partial_object_retrieval_with_start_range(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            206,
            'should retrieve a partial object from the middle to the end')

    def test_partial_object_retrieval_with_end_range(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            206,
            'should retrieve a partial object from the end to the middle')

    def test_partial_object_retrieval_with_range(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            206,
            'should retrieve a partial object from the middle to the'
            ' middle')

    def test_partial_object_retrieval_with_complete_range(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            200,
            'should retrieve complete object')

    def test_object_creation_with_valid_object_name(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        self.assertEqual(
            response.status_code,
            201,
            'should create object.')

    def test_object_update_with_valid_object_name(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 201, 'should update object.')

    def test_object_creation_with_etag_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 201, 'should create object')

    def test_object_creation_with_metadata(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            201,
            'should create object with metadata')

    def test_object_creation_with_dynamic_large_object(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            201,
            'should create object representing segment 1')

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

        self.assertEqual(
            response.status_code,
            201,
            'should create object representing segment 2')

        large_object_common_prefix = '{0}/{1}'.format(
            container_name, object_name)

        headers = {'Content-Length': '0',
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Manifest': large_object_common_prefix}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers)

        self.assertEqual(
            response.status_code,
            201,
            'should create large object manifest')

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(
            response.status_code,
            200,
            'should retrieve assembled large file')

    def test_object_creation_with_cors_allow_credentials_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Credentials': 'true'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(
            response.status_code,
            200,
            'should retrieve object')

    def test_object_creation_with_cors_access_control_allow_methods(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
                container_name,
                object_name)

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_creation_with_cors_allow_origin_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Allow-Origin': 'http://foobar.org'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_creation_with_cors_expose_headers_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Expose-Headers': 'X-Foobar-Header'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_creation_with_cors_max_age_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Max-Age': '5'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_creation_with_cors_request_headers_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Request-Headers': 'x-requested-with'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_creation_with_cors_request_method_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Access-Control-Request-Method': 'GET'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_creation_with_cors_origin_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Origin': 'http://foobar.org'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(response.status_code, 200, 'should retrieve object')

    def test_object_retrieval_with_file_compression(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Uncompressed test file data'
        compressed_object_data = zlib.compress(object_data)
        content_length = str(len(compressed_object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Encoding': 'gzip'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=compressed_object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(
            response.status_code,
            200,
            'should retrieve a compressed object')

    def test_object_retrieval_with_browser_bypass(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Disposition': 'attachment; filename=testdata.txt'}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(
            response.status_code,
            200,
            'should retrieve object')

    def test_object_creation_with_scheduled_expiration(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            201,
            'should create an object scheduled to expire')

    def test_object_creation_with_delete_after_header(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(
            response.status_code,
            201,
            'should create an object scheduled to expire')

    def test_versioned_container_creation_with_valid_data(self):
        #Create a container for 'non-current' object storage
        non_current_version_container_name = self.setup_container(
            self.base_container_name)

        #Create a container for 'current' object storage
        current_version_container_headers = \
            {'X-Versions-Location': non_current_version_container_name}
        current_version_container_name = self.setup_container(
            self.base_container_name,
            headers=current_version_container_headers)

        #Create an object (version 1)
        object_name = self.base_object_name

        object_data = 'Version 1'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            current_version_container_name,
            object_name,
            headers=headers,
            data=object_data)

        self.assertEqual(
            response.status_code,
            201,
            'should create versioned object')

        response = self.client.list_objects(
            non_current_version_container_name)

        self.assertEqual(response.status_code, 204, 'should be empty')

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

        self.assertEqual(
            response.status_code,
            201,
            'should update versioned object')

        response = self.client.list_objects(
            non_current_version_container_name)

        self.assertEqual(response.status_code, 200, 'should have files')

    def test_put_copy_object(self):
        src_container_name = self.setup_container(self.base_container_name)
        dest_container_name = self.setup_container(self.base_container_name)

        src_obj_name = self.base_object_name

        object_data = 'Test file data'
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            src_container_name,
            src_obj_name,
            headers=headers,
            data=object_data)

        dest_obj_name = self.base_object_name

        source = '/{0}/{1}'.format(src_container_name, src_obj_name)

        hdrs = {'X-Copy-From': source, 'Content-Length': '0'}

        response = self.client.copy_object(
            dest_container_name,
            dest_obj_name,
            headers=hdrs)

        self.assertEqual(
            response.status_code,
            201,
            'should copy an existing object')

        response = self.client.get_object(
            dest_container_name,
            dest_obj_name)

        self.assertEqual(
            response.status_code,
            200,
            'should be accessible after copy')

    def test_copy_object(self):
        src_container_name = self.setup_container(self.base_container_name)
        dest_container_name = self.setup_container(self.base_container_name)

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

        dest_obj_name = self.base_object_name

        dest = '/{0}/{1}'.format(dest_container_name, dest_obj_name)

        hdrs = {'Destination': dest}

        response = self.client.copy_object(
            src_container_name,
            src_obj_name,
            headers=hdrs)

        self.assertEqual(
            response.status_code,
            201,
            'should copy an existing object')

        response = self.client.get_object(
            dest_container_name,
            dest_obj_name)

        self.assertEqual(
            response.status_code,
            200,
            'should be accessible after copy')

    def test_object_deletion_with_valid_object(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 204, 'should be deleted')

        response = self.client.get_object(
            container_name,
            object_name)

        self.assertEqual(
            response.status_code,
            404,
            'should not be accessible after deletion')

    def test_metadata_retrieval_with_newly_created_object(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 201, 'should be created')

        response = self.client.get_object_metadata(
            container_name,
            object_name)

        self.assertEqual(
            response.status_code,
            200,
            'should be accessible after creation')

    def test_metadata_retrieval_with_object_possessing_metadata(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 202, 'should set metadata')

    def test_object_update_with_metadata(self):
        container_name = self.setup_container(self.base_container_name)
        object_name = self.base_object_name

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

        self.assertEqual(response.status_code, 202, 'should set metadata')

        response = self.client.get_object_metadata(
            container_name,
            object_name)

        self.assertEqual(
            response.status_code,
            200,
            'should be accessible after update')
