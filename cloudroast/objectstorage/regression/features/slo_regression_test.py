"""
Copyright 2014 Rackspace

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

from random import choice
from hashlib import md5

from cafe.common.unicode import UNICODE_BLOCKS, BLOCK_NAMES
from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

CONTAINER_DESCRIPTOR = 'static_large_object_regression_test'


class StaticLargeObjectRegressionTest(ObjectStorageFixture):

    @classmethod
    def setUpClass(cls):
        super(StaticLargeObjectRegressionTest, cls).setUpClass()

        cls.min_segment_size = \
            cls.objectstorage_api_config.min_slo_segment_size
        cls.object_name = Constants.VALID_OBJECT_NAME
        cls.data_pool = [char for char in UNICODE_BLOCKS.get_range(
            BLOCK_NAMES.basic_latin).encoded_codepoints()]
        cls.num_segments = 3

    def test_slo_creation_in_diff_containers(self):
        """
        Scenario:
            Create a SLO where the manifest and each segment are in their
            own unique containers.

        Expected Results:
            The SLO should be created.
            The ETAG for the SLO should be the md5 sum of the
            concatenated ETAGs for all the segments.
            The Content-Length for the SLO should be the sum of the
            content-length of all the segments.
            The header x-static-large-object should be in the headers for
            the SLO.
        """

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = self.object_name
        object_etag = ''
        object_size = 0

        slo_manifest = []
        for x in range(0, self.num_segments):
            segment_container_name = self.create_temp_container(
                '{0}_{1}'.format('slo_segment', x))
            segment_name = '{0}_{1}'.format(self.object_name, x)
            segment_data = ''.join([choice(self.data_pool) for x in xrange(
                self.min_segment_size)])
            segment_etag = md5(segment_data).hexdigest()
            object_etag += segment_etag
            object_size += len(segment_data)

            segment_response = self.client.create_object(
                segment_container_name,
                segment_name,
                data=segment_data)
            self.assertTrue(segment_response.ok,
                            msg="Creating segment for SLO; Expected "
                            "to receive a status code of 201 received a code "
                            "of {0}".format(segment_response.status_code))

            slo_manifest.append({
                'path': '/{0}/{1}'.format(
                    segment_container_name, segment_name),
                'etag': segment_etag,
                'size_bytes': self.min_segment_size})

        manifest_response = self.behaviors.create_static_large_object(
            container_name, object_name, manifest=slo_manifest)
        self.assertTrue(manifest_response.ok,
                        msg="Creating a SLO in different containers; Expected "
                            "to receive a status code of 201 received a code "
                            "of {0}".format(manifest_response.status_code))

        slo_response = self.client.get_object(container_name, object_name)
        object_etag = '"{0}"'.format(md5(object_etag).hexdigest())

        self.assertEqual(int(slo_response.headers.get('content-length')),
                         object_size,
                         msg="The content-length of the SLO {0} did not "
                             "match the sum of it's segments {1}".format(
                                 slo_response.headers.get('content-length'),
                                 object_size))

        self.assertEqual(slo_response.headers.get('etag'),
                         object_etag,
                         msg="The SLO manifest etag {0} did not match the "
                             "calculated etag of it's segements {1}".format(
                                 slo_response.headers.get('etag'),
                                 object_etag))

        self.assertIn("x-static-large-object",
                      slo_response.headers,
                      msg="Could not find header {0} in SLO manifest "
                          "response headers {1}".format(
                              "x-static-large-object", slo_response.headers))
