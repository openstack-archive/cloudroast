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

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
CONTAINER_NAME = 'list_limit_test_container'


class ListLimitTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ListLimitTest, cls).setUpClass()

        cls.container_name = CONTAINER_NAME
        cls.client.create_container(cls.container_name)

        object_data = 'Test file data'
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        cls.obj_names = ["a_obj", "b_obj", "c_obj"]

        for obj_name in cls.obj_names:
            cls.client.create_object(
                cls.container_name,
                obj_name,
                headers=headers,
                data=object_data)

    @classmethod
    def tearDownClass(cls):
        super(ListLimitTest, cls).setUpClass()
        cls.behaviors.force_delete_containers([cls.container_name])

    def test_list_limit(self):
        params = {"limit": "2", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member.keys():
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = 2
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertIn("a_obj", members, msg="a_obj was not in the response")
        self.assertIn("b_obj", members, msg="b_obj was not in the response")

    def test_list_limit_zero(self):
        params = {"limit": "0", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = json.loads(response.content)

        members = []
        for member in content:
            if 'name' in member.keys():
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = 0
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
