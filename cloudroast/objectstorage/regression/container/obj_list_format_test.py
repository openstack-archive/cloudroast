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

CONTENT_TYPE_TEXT = 'text/plain; charset=utf-8'
CONTENT_TYPE_XML = 'application/xml; charset=utf-8'
CONTENT_TYPE_JSON = 'application/json; charset=utf-8'
CONTAINER_NAME = 'list_format_test_container'


class ListFormatTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ListFormatTest, cls).setUpClass()

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
        super(ListFormatTest, cls).setUpClass()
        cls.client.force_delete_containers([cls.container_name])

    def test_list_format_text(self):
        response = self.client.list_objects(self.container_name)

        self.assertTrue(response.ok)

        expected = CONTENT_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="expected content-type {0} recieved {1}".format(
                expected,
                recieved))

        self.assertEqual(len(response.entity), len(self.obj_names))

        for storage_obj in response.entity:
            self.assertIn(storage_obj.name, self.obj_names)

    def test_list_format_json(self):
        params = {"format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        expected = CONTENT_TYPE_JSON
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="expected content-type {0} recieved {1}".format(
                expected,
                recieved))

        self.assertEqual(len(response.entity), len(self.obj_names))

        for storage_obj in response.entity:
            self.assertIn(storage_obj.name, self.obj_names)

    def test_list_format_xml(self):
        params = {"format": "xml"}
        response = self.client.list_objects(self.container_name, params=params)

        self.assertTrue(response.ok)

        expected = CONTENT_TYPE_XML
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="expected content-type {0} recieved {1}".format(
                expected,
                recieved))

        self.assertEqual(len(response.entity), len(self.obj_names))

        for storage_obj in response.entity:
            self.assertIn(storage_obj.name, self.obj_names)
