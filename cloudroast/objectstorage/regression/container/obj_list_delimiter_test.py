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

CONTENT_TYPE_TEXT = "text/plain; charset=UTF-8"
CONTAINER_NAME = 'list_delimiter_test_container'


class DelimiterTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(DelimiterTest, cls).setUpClass()

        cls.container_name = CONTAINER_NAME
        cls.client.create_container(cls.container_name)

        cls.object_data = cls.behaviors.VALID_OBJECT_DATA
        cls.content_length = str(len(cls.object_data))
        cls.headers = {"Content-Length": cls.content_length,
                       "Content-Type": CONTENT_TYPE_TEXT}

    @classmethod
    def tearDownClass(cls):
        super(DelimiterTest, cls).setUpClass()
        cls.client.force_delete_containers([cls.container_name])

    def test_delimeter(self):
        obj0_name = "x0/y"
        obj1_name = "x1"
        obj2_name = "x2/"

        self.client.create_object(
            self.container_name,
            obj0_name,
            headers=self.headers,
            data=self.object_data)

        self.client.create_object(
            self.container_name,
            obj1_name,
            headers=self.headers,
            data=self.object_data)

        self.client.create_object(
            self.container_name,
            obj2_name,
            headers=self.headers,
            data=self.object_data)

        params = {"delimiter": "/", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, e:
            print e

        members = []
        for member in content:
            if "subdir" in member.keys():
                members.append(member["subdir"])
            elif "name" in member.keys():
                members.append(member["name"])
            else:
                continue

        expected = 3
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertIn(
            'x0/',
            members,
            msg="x0/ was not in the response")
        self.assertIn(
            'x1',
            members,
            msg="x1 was not in the response")
        self.assertIn(
            'x2/',
            members,
            msg="x2/ was not in the response")

        self.addCleanup(
            self.client.delete_object,
            self.container_name,
            obj2_name)

        self.addCleanup(
            self.client.delete_object,
            self.container_name,
            obj1_name)

        self.addCleanup(
            self.client.delete_object,
            self.container_name,
            obj0_name)
