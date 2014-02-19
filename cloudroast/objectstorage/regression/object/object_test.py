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
import unittest
from calendar import timegm
from time import gmtime, sleep

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools.check_dict import get_value

CONTAINER_NAME = 'object_regression'


class ObjectRegressionTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ObjectRegressionTest, cls).setUpClass()

        cls.base_container_name = CONTAINER_NAME
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.default_obj_data = cls.behaviors.VALID_OBJECT_DATA
        cls.expirer_run_interval = \
            cls.objectstorage_api_config.object_expirer_run_interval

    @unittest.skipUnless(get_value('slow') == 'true', 'test is slow')
    def test_object_deletion_with_x_delete_at(self):
        """
        Scenario:
            Create an object which has the X-Delete-At metadata.

        Expected Results:
            The object should be accessible before the 'delete at' time.
            The object should not be accessible after the 'delete at' time.
            The object should not be listed after the object expirer has had
                time to run.

        NOTE:
            This is currently a bug and has not yet been fixed.
            https://bugs.launchpad.net/swift/+bug/1257330
        """
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        delete_after = 60
        delete_at = str(int(timegm(gmtime()) + delete_after))
        headers = {'Content-Length': str(len(self.default_obj_data)),
                   'X-Delete-At': delete_at}

        resp = self.client.create_object(
            container_name, self.default_obj_name,
            headers=headers, data=self.default_obj_data)

        self.assertEqual(
            201, resp.status_code,
            'Object should be created with X-Delete-At header.')

        resp = self.client.get_object(container_name, self.default_obj_name)

        self.assertEqual(
            200, resp.status_code,
            'Object should exist before X-Delete-At.')

        # wait for the object to be deleted.
        sleep(delete_after)

        resp = self.client.get_object(container_name, self.default_obj_name)

        self.assertEqual(
            404, resp.status_code,
            'Object should be deleted after X-Delete-At.')

        sleep(self.expirer_run_interval)

        get_response = self.client.list_objects(
            container_name,
            params={'format': 'json'})

        self.assertEqual(
            204, get_response.status_code,
            'No content should be returned for the request.')

        get_count = int(get_response.headers.get('x-container-object-count'))

        self.assertEqual(
            '0', get_count,
            'No objects should be listed in the container.')

        self.assertEqual(
            '0', len(get_response.entity),
            'No objects should be listed in the container.')

        head_response = self.client.get_container_metadata(container_name)

        head_count = int(head_response.headers.get('x-container-object-count'))

        self.assertEqual(
            '0', head_count,
            'No objects should be listed in the container.')
