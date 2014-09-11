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
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

CONTAINER_NAME = 'container_quota_test_container'


class ContainerQuotaTest(ObjectStorageFixture):
    def tearDown(self):
        self.behaviors.force_delete_containers([CONTAINER_NAME])

    def test_set_container_quota_bytes_header(self):
        """
        Scenario:
        'X-Container-Meta-Quota-Bytes' is set on a container

        Expected Results:
        container HEAD request returns the
        'X-Container-Meta-Quota-Bytes' header and it is set
        properly
        """
        container_bytes = '1024'
        hdrs = {'X-Container-Meta-Quota-Bytes': container_bytes}
        response = self.client.create_container(CONTAINER_NAME, headers=hdrs)

        self.assertTrue(
            response.ok,
            msg=("container created with x-container-meta-quota-bytes"
                 " header returned status code {0}").format(
                response.status_code))

        response = self.client.get_container_metadata(CONTAINER_NAME)

        expected = container_bytes
        received = response.headers.get('x-container-meta-quota-bytes')

        self.assertEqual(
            expected,
            received,
            msg=("x-container-meta-quota-bytes header was not set properly."
                 " expected: {0} received: {1}").format(expected, received))

    def test_set_container_quota_count_header(self):
        """
        Scenario:
        'X-Container-Meta-Quota-Count' is set on a container

        Expected Results:
        container HEAD request returns the
        'X-Container-Meta-Quota-Count' header and it is set
        properly
        """
        num_objects = 10
        hdrs = {'X-Container-Meta-Quota-Count': num_objects}
        self.client.create_container(CONTAINER_NAME, headers=hdrs)
        response = self.client.get_container_metadata(CONTAINER_NAME)

        self.assertTrue(
            response.ok,
            msg=("container created with x-container-meta-quota-count"
                 " header returned status code {0}").format(
                response.status_code))

        expected = str(num_objects)
        received = response.headers.get('x-container-meta-quota-count')

        self.assertEqual(
            expected,
            received,
            msg=("x-container-meta-quota-count header was not set properly."
                 " expected: {0} received: {1}").format(expected, received))
