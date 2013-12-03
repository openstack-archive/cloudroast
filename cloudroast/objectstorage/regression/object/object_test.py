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
import time
import unittest
from calendar import timegm
from time import gmtime

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools.check_dict import get_value

CONTAINER_NAME = 'object_regression'
EXPIRER_RUN_INTERVAL = 300


class ObjectRegressionTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ObjectRegressionTest, cls).setUpClass()

        cls.base_container_name = CONTAINER_NAME
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.default_obj_data = cls.behaviors.VALID_OBJECT_DATA

    @unittest.skipUnless(get_value('slow') == 'true', 'test is too slow')
    def test_object_deletion_with_x_delete_at(self):
        """
        Scenario:
            Create an object which has the X-Delete-At metadata.

        Expected Results:
            The object should be accessible before the 'delete at' time.
            The object should not be accessible after the 'delete at' time.
            The object should not be listed after the object expirer has had
                time to run.
        """
        container_name = self.behaviors.generate_unique_container_name(
            self.base_container_name)

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers, [container_name])

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

        resp = self.client.get_object(
            container_name,
            self.default_obj_name)

        self.assertEqual(
            200, resp.status_code,
            'Object should exist before X-Delete-At.')

        # wait for the object to be deleted.
        time.sleep(delete_after)

        resp = self.client.get_object(
            container_name,
            self.default_obj_name)

        self.assertEqual(
            404, resp.status_code,
            'Object should be deleted after X-Delete-At.')

        resp = self.client.list_objects(
            container_name)

        # wait for the object to be removed from container listings.
        time.sleep(EXPIRER_RUN_INTERVAL * 2)

        self.assertEqual(
            204, resp.status_code,
            'No objects should be listed in the container.')
