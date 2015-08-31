"""
Copyright 2015 Rackspace

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
from cloudcafe.common.tools import randomstring as randstring
from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

CONTENT_TYPE_TEXT = "text/plain; charset=UTF-8"
CONTAINER_NAME = "object_versioning_test"
BASE_DATA = "Version_"


class ObjectVersioningTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(ObjectVersioningTest, cls).setUpClass()

        cls.container_name = CONTAINER_NAME
        cls.object_name = "{0}_{1}".format(
            Constants.VALID_OBJECT_NAME,
            randstring.get_random_string())

    def setUp(self):
        super(ObjectVersioningTest, self).setUp()
        """
        Create a container for "current" object storage
        """
        self.current_version_container_name = (
            self.create_temp_container(
                "current_container_{0}".format(self.container_name)))

        """
        Create a container for "non-current" object storage
        """
        self.non_current_version_container_name = (
            self.create_temp_container(
                "non_current_container_{0}".format(self.container_name)))

        headers = (
            {"X-Versions-Location": self.non_current_version_container_name})
        self.client.set_container_metadata(
            self.current_version_container_name, headers=headers)

        self.num_objects = 4
        self.num_versioned_objects = self.num_objects - 1

        self.object_data_version0 = "{0}0".format(BASE_DATA)
        self.object_data_version1 = "{0}1".format(BASE_DATA)
        self.object_data_version2 = "{0}2".format(BASE_DATA)
        self.object_data_version3 = "{0}3".format(BASE_DATA)

        """
        create objects in the current version container
        """
        for i in range(0, self.num_objects):
            data = eval("self.object_data_version{0}".format(i))

            headers = {"X-Object-Meta-Version": data,
                       "Content-Length": str(len(data)),
                       "Content-Type": CONTENT_TYPE_TEXT}

            self.client.create_object(
                self.current_version_container_name,
                self.object_name,
                headers=headers,
                data=eval("self.object_data_version{0}".format(i)))

    def get_prefix(self, obj_name):
        """
        Naming Schema: Non-current versions are assigned the name
        <length><object_name>/<timestamp>, where length is the 3-character
        zero-padded hexadecimal character length of the <object_name>
        """
        prefix = None
        padded_hex = None
        temp = str(hex(len(obj_name))).split("x")[1]
        if len(temp) == 1:
            padded_hex = "00{0}".format(temp)
        elif len(temp) == 2:
            padded_hex = "0{0}".format(temp)
        else:
            padded_hex = temp

        prefix = "{0}{1}".format(padded_hex, obj_name)

        return prefix

    @ObjectStorageFixture.required_features('object_versioning')
    def test_versioned_obj_creation_with_valid_data(self):
        """
        check the current version object content
        """
        response = self.client.get_object(
            self.current_version_container_name,
            self.object_name)

        expected = self.object_data_version3
        received = response.content

        self.assertEqual(
            expected,
            received,
            msg="retrieving current version of object expected content: {0}"
                " recieved content: {1}".format(expected, received))

        """
        check the number of versioned objects
        """
        params = {"format": "json"}
        response = self.client.list_objects(
            self.non_current_version_container_name,
            params=params)

        resp_obj_count = response.headers.get("x-container-object-count")

        expected = self.num_versioned_objects
        received = int(resp_obj_count)

        self.assertEqual(
            expected,
            received,
            msg="obj list on non-current version container expected: {0}"
                " objects. response contained: {1} objects".format(
                    expected,
                    received))

        object_names = [obj.name for obj in response.entity]

        expected_prefix = self.get_prefix(self.object_name)

        for i in range(0, self.num_versioned_objects):
            obj_name = object_names[i]

            """
            check for a slash in the name of the versioned object
            """
            tokens = obj_name.split('/')

            expected = 2
            received = len(tokens)

            self.assertEqual(
                expected,
                received,
                msg="slash is present in the versioned object name")

            """
            check the prefix of the versioned object
            """
            current_name_prefix = tokens[0]

            expected = expected_prefix
            received = current_name_prefix

            self.assertEqual(
                expected,
                received,
                msg="versioned object prefix expected: {0}"
                    " recieved: {1}".format(expected, received))

            """
            check the content of the versioned object
            """
            response = self.client.get_object(
                self.non_current_version_container_name,
                obj_name)

            expected = eval("self.object_data_version{0}".format(i))
            received = response.content

            self.assertEqual(
                expected,
                received,
                msg="retrieving current version of object expected"
                    " content: {0} recieved content: {1}".format(
                        expected,
                        received))

            """
            check the X-Object-Meta-Version value of the versioned obj
            """
            expected = eval("self.object_data_version{0}".format(i))
            received = response.headers.get("X-Object-Meta-Version")

            self.assertEqual(
                expected,
                received,
                msg="versioned object metadata expected"
                    " X-Object-Meta-Version: {0} recieved"
                    " X-Object-Meta-Version: {1}".format(
                        expected,
                        received))

        """
        update current version metadata
        """
        headers = {"X-Object-Meta-Foo": "Bar"}

        response = self.client.set_object_metadata(
            self.current_version_container_name,
            self.object_name,
            headers=headers)

        self.assertTrue(
            response.ok,
            msg="current obj metadata update was successful")

        """
        check the number of versioned objects
        """
        response = self.client.list_objects(
            self.non_current_version_container_name,
            params=params)

        resp_obj_count = response.headers.get("x-container-object-count")

        expected = self.num_versioned_objects
        received = int(resp_obj_count)

        self.assertEqual(
            expected,
            received,
            msg="obj list on non-current version container after metadata"
                " update on current version obj expected: {0}"
                " objects. response contained: {1} objects".format(
                    expected,
                    received))

    @ObjectStorageFixture.required_features('object_versioning')
    def test_versioned_obj_deletion_with_valid_data(self):
        num_deletes = 0
        for i in reversed(range(0, self.num_versioned_objects)):
            self.client.delete_object(
                self.current_version_container_name,
                self.object_name)

            """
            check that the obj data in the current version container is the
            previous version after deleting current obj
            """
            response = self.client.get_object(
                self.current_version_container_name,
                self.object_name)

            expected = eval("self.object_data_version{0}".format(i))
            received = response.content

            self.assertEqual(
                expected,
                received,
                msg="retrieving current version of object expected"
                    " content: {0} recieved content: {1}".format(
                        expected,
                        received))

            """
            check the X-Object-Meta-Version value of the previous obj after
            deleting the current obj
            """
            expected = eval("self.object_data_version{0}".format(i))
            received = response.headers.get("X-Object-Meta-Version")

            self.assertEqual(
                expected,
                received,
                msg="current version object metadata expected"
                    " content: {0} recieved content: {1}".format(
                        expected,
                        received))

            """
            check the number of objects in the current container
            """
            response = self.client.list_objects(
                self.current_version_container_name)

            resp_obj_count = response.headers.get("x-container-object-count")

            expected = 1
            received = int(resp_obj_count)

            self.assertEqual(
                expected,
                received,
                msg="obj list on current version container after delete "
                    "expected: {0} object. response contained:"
                    " {1} object(s)".format(
                        expected,
                        received))

            num_deletes += 1

        """
        check the number of versioned objects in the non-current container
        """
        response = self.client.list_objects(
            self.non_current_version_container_name)

        resp_obj_count = response.headers.get("x-container-object-count")

        expected = self.num_versioned_objects - num_deletes
        received = int(resp_obj_count)

        self.assertEqual(
            expected,
            received,
            msg="obj list on non-current version container expected: {0}"
                " objects. response contained: {1} objects".format(
                    expected,
                    received))

        """
        check the number of objects in the current container after final delete
        """
        self.client.delete_object(
            self.current_version_container_name,
            self.object_name)

        response = self.client.list_objects(
            self.non_current_version_container_name)

        resp_obj_count = response.headers.get("x-container-object-count")

        expected = 0
        received = int(resp_obj_count)

        self.assertEqual(
            expected,
            received,
            msg="obj list on current version container after final delete"
                " expected: {0} objects. response contained:"
                " {1} objects".format(expected, received))

    @ObjectStorageFixture.required_features('object_versioning')
    def test_disable_object_versioning(self):
        object_data_version4 = "{0}4".format(BASE_DATA)

        """
        check the number of versioned objects
        """
        response = self.client.list_objects(
            self.non_current_version_container_name)

        resp_obj_count = response.headers.get("x-container-object-count")

        expected = self.num_versioned_objects
        received = int(resp_obj_count)

        self.assertEqual(
            expected,
            received,
            msg="obj list on non-current version container expected: {0}"
                " objects. response contained: {1} objects".format(
                    expected,
                    received))

        """
        disable obj versioning and create a new obj in the current version
        container
        """
        headers = {"X-Versions-Location": ""}

        response = self.client.set_container_metadata(
            self.current_version_container_name,
            headers=headers)

        self.assertTrue(
            response.ok,
            msg="disabeling versioning was successful")

        headers = {"X-Object-Meta-Version": object_data_version4,
                   "Content-Length": str(len(object_data_version4)),
                   "Content-Type": CONTENT_TYPE_TEXT}

        response = self.client.create_object(
            self.current_version_container_name,
            self.object_name,
            headers=headers,
            data=object_data_version4)

        self.assertTrue(
            response.ok,
            msg="obj creation after disabeling versioning was successful")

        """
        check the number of versioned objects
        """
        response = self.client.list_objects(
            self.non_current_version_container_name)

        resp_obj_count = response.headers.get("x-container-object-count")

        expected = self.num_versioned_objects
        received = int(resp_obj_count)

        self.assertEqual(
            expected,
            received,
            msg="obj list on non-current version container after disabeling"
                " versioning expected: {0} objects. response contained:"
                " {1} objects".format(
                    expected,
                    received))
