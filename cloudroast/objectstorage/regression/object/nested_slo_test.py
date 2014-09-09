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

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.objectstorage.generators import ObjectStorageGenerator

CONTAINER_DESCRIPTOR = 'object_smoke_test'
STATUS_CODE_MSG = ('{method} expected status code {expected}'
                   ' received status code {received}')


class NestedSLOTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(NestedSLOTest, cls).setUpClass()
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.nested_obj_name = "nested_slo"
        cls.generator = ObjectStorageGenerator(cls.client)
        cls.nested_object_count = 5

    def test_nested_slo_creation_same_container(self):
        """
        Scenario:
            Create an SLO of SLOs that are all in the same container and then
            retrieve the nested SLO.

        Expected Results:
            Object retrieval should return a 200 and the sumation of all
            the segment sizes should equal the retrieved object length.
        """
        manifest = []
        nested_slo_size = 0

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        for i in range(self.nested_object_count):
            slo = self.generator.generate_static_large_object(
                container_name, "{0}_{1}".format(self.default_obj_name, i))

            manifest.append(
                {'path': "/{0}/{1}_{2}".format(container_name,
                                               self.default_obj_name,
                                               i),
                 'etag': slo.get("etag"),
                 'size_bytes': slo.get("size")})
            nested_slo_size += slo.get("size")

        self.client.create_object(
            container_name,
            self.nested_obj_name,
            data=json.dumps(manifest),
            params={'multipart-manifest': 'put'})

        object_response = self.client.get_object(
            container_name, self.nested_obj_name)

        method = 'Nested Static Large Object Retrieval'
        expected = 200
        received = object_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        self.assertEqual(
            nested_slo_size,
            int(object_response.headers.get("content-length")),
            msg="Nested SLO size {0} does not equal sumation of segment "
                "sizes {1}".format(nested_slo_size,
                                   object_response.headers.get(
                                       "content-length")))

    def test_nested_slo_creation_different_containers(self):
        """
        Scenario:
            Create an SLO of SLOs that are in different containers and then
            retrieve the nested SLO.

        Expected Results:
            Object retrieval should return a 200 and the sumation of all
            the segment sizes should equal the retrieved object length.
        """
        manifest = []
        nested_slo_size = 0

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        for i in range(self.nested_object_count):
            loop_container_name = self.create_temp_container(
                descriptor=CONTAINER_DESCRIPTOR)

            slo = self.generator.generate_static_large_object(
                loop_container_name,
                "{0}_{1}".format(self.default_obj_name, i))

            manifest.append(
                {'path': "/{0}/{1}_{2}".format(loop_container_name,
                                               self.default_obj_name,
                                               i),
                 'etag': slo.get("etag"),
                 'size_bytes': slo.get("size")})
            nested_slo_size += slo.get("size")

        self.client.create_object(
            container_name,
            "nested_slo",
            data=json.dumps(manifest),
            params={'multipart-manifest': 'put'})

        object_response = self.client.get_object(container_name, "nested_slo")

        method = 'Nested Static Large Object Retrieval'
        expected = 200
        received = object_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        self.assertEqual(
            nested_slo_size,
            int(object_response.headers.get("content-length")),
            msg="Nested SLO size {0} does not equal sumation of segment "
                "sizes {1}".format(nested_slo_size,
                                   object_response.headers.get(
                                       "content-length")))
