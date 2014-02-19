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
from cafe.drivers.unittest.decorators import data_driven_test
from cafe.drivers.unittest.decorators import DataDrivenFixture
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cafe.drivers.unittest.datasets import DatasetList

CONTENT_TYPE_TEXT = "text/plain; charset=utf-8"
CONTENT_TYPE_XML = "application/xml; charset=utf-8"
CONTENT_TYPE_JSON = "application/json; charset=utf-8"
CONTAINER_NAME = "list_format_test_container"


data_set_list = DatasetList()

data_set_list.append_new_dataset(
    "text",
    {"content_type": CONTENT_TYPE_TEXT, "headers": {}})

data_set_list.append_new_dataset(
    "json_header",
    {"content_type": CONTENT_TYPE_JSON,
     "headers": {"Accept": CONTENT_TYPE_JSON}})

data_set_list.append_new_dataset(
    "json_param",
    {"content_type": CONTENT_TYPE_JSON, "params": {"format": "json"}})

data_set_list.append_new_dataset(
    "xml_header",
    {"content_type": CONTENT_TYPE_XML,
     "headers": {"Accept": CONTENT_TYPE_XML}})

data_set_list.append_new_dataset(
    "xml_param",
    {"content_type": CONTENT_TYPE_XML, "params": {"format": "xml"}})


@DataDrivenFixture
class ListFormatTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ListFormatTest, cls).setUpClass()

        cls.container_name = cls.behaviors.generate_unique_container_name(
            "listformat")

        cls.client.create_container(cls.container_name)

        object_data = "Test file data"
        content_length = str(len(object_data))
        headers = {"Content-Length": content_length,
                   "Content-Type": CONTENT_TYPE_TEXT}

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
        cls.behaviors.force_delete_containers([cls.container_name])

    @data_driven_test(data_set_list)
    def ddtest_object_list_format(self, content_type=None, headers=None,
                                  params=None):

        response = self.client.list_objects(
            self.container_name,
            headers=headers,
            params=params)

        expected = content_type
        received = response.headers.get("content-type")
        self.assertEqual(
            expected,
            received,
            msg="expected content-type {0} received {1}".format(
                expected,
                received))

        expected = len(self.obj_names)
        received = len(response.entity)
        self.assertEqual(
            expected,
            received,
            msg="expected {0} objects received {1} objects".format(
                str(expected),
                str(received)))

        for storage_obj in response.entity:
            self.assertIn(storage_obj.name, self.obj_names)
