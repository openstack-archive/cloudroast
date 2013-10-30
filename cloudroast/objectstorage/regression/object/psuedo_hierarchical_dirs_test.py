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

from cloudcafe.common.tools import randomstring as randstring
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

CONTENT_TYPE_TEXT = "text/plain; charset=UTF-8"
CONTAINER_NAME = "psuedo_dirs_test"


class PsuedoHierarchalDirsTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(PsuedoHierarchalDirsTest, cls).setUpClass()
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.default_obj_data = cls.behaviors.VALID_OBJECT_DATA

    def get_members(self, keys, response_content):
        members = []
        content = None

        try:
            content = json.loads(response_content)
        except ValueError, error:
            self.fixture_log.exception(error)

        for current in content:
            for key in keys:
                if key in current.keys():
                    members.append(current[key])
                else:
                    continue

        return members

    def test_psuedo_dirs_delimiter_test(self):
        container_name = "{0}_{1}".format(
            CONTAINER_NAME,
            randstring.get_random_string())

        obj_names = {"/": "music/grok",
                     "-": "music-drok",
                     ">": "music>foo",
                     "|": "music|bar"}

        content_length = str(len(self.default_obj_data))
        headers = {"Content-Length": content_length,
                   "Content-Type": CONTENT_TYPE_TEXT}

        for key in obj_names.keys():
            self.behaviors.create_object(
                container_name,
                obj_names.get(key),
                data=self.default_obj_data,
                headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        for delimiter in obj_names.keys():
            prefix = "music{0}".format(delimiter)

            params = {"prefix": prefix,
                      "delimiter": delimiter,
                      "format": "json"}
            response = self.client.list_objects(container_name, params=params)

            members = self.get_members(["subdir", "name"], response.content)

            expected = 1
            recieved = len(members)
            self.assertEqual(
                expected,
                recieved,
                msg="container list with prefix: {0} and delimiter: {1}"
                " expected: {2} members recieved: {3}".format(
                    prefix,
                    delimiter,
                    expected,
                    recieved))

            obj_name = obj_names.get(delimiter)
            self.assertIn(
                obj_name,
                members,
                msg="object name: {0} was not found in response body:"
                " {1}".format(obj_name, members))

    def test_psuedo_dirs_traversal(self):
        container_name = "{0}_{1}".format(
            CONTAINER_NAME,
            randstring.get_random_string())

        content_length = str(len(self.default_obj_data))
        headers = {"Content-Length": content_length,
                   "Content-Type": CONTENT_TYPE_TEXT}

        base_name = "music/the_best_of_grok_and_drok/grok_live/"

        vol1_obj1 = "{0}{1}".format(base_name, "vol_1/rage_against_the_foo")
        vol1_obj2 = "{0}{1}".format(base_name, "vol_1/a_fist_full_of_foo")
        vol1_obj3 = "{0}{1}".format(base_name, "vol_1/nevermind_the_foo")
        vol2_obj1 = "{0}{1}".format(base_name, "vol_2/iron_foo")
        vol2_obj2 = "{0}{1}".format(base_name, "vol_2/foo_master")

        self.behaviors.create_object(
            container_name,
            vol1_obj1,
            data=self.default_obj_data,
            headers=headers)

        self.behaviors.create_object(
            container_name,
            vol1_obj2,
            data=self.default_obj_data,
            headers=headers)

        self.behaviors.create_object(
            container_name,
            vol1_obj3,
            data=self.default_obj_data,
            headers=headers)

        self.behaviors.create_object(
            container_name,
            vol2_obj1,
            data=self.default_obj_data,
            headers=headers)

        self.behaviors.create_object(
            container_name,
            vol2_obj2,
            data=self.default_obj_data,
            headers=headers)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        delimiter = "/"

        prefix = "music/"
        params = {"prefix": prefix, "delimiter": delimiter, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["subdir", "name"], response.content)

        expected = 1
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with prefix: {0} and delimiter: {1}"
            " expected: {2} members recieved: {3}".format(
                prefix,
                delimiter,
                expected,
                recieved))

        obj_name = "music/the_best_of_grok_and_drok/"
        self.assertIn(
            obj_name,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(obj_name, members))

        prefix = "music/the_best_of_grok_and_drok/"
        params = {"prefix": prefix, "delimiter": delimiter, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["subdir", "name"], response.content)

        expected = 1
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with prefix: {0} and delimiter: {1}"
            " expected: {2} members recieved: {3}".format(
                prefix,
                delimiter,
                expected,
                recieved))

        obj_name = "music/the_best_of_grok_and_drok/grok_live/"
        self.assertIn(
            obj_name,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(obj_name, members))

        prefix = "music/the_best_of_grok_and_drok/grok_live/"
        params = {"prefix": prefix, "delimiter": delimiter, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["subdir", "name"], response.content)

        expected = 2
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with prefix: {0} and delimiter: {1}"
            " expected: {2} members recieved: {3}".format(
                prefix,
                delimiter,
                expected,
                recieved))

        obj_name = "music/the_best_of_grok_and_drok/grok_live/vol_1/"
        self.assertIn(
            obj_name,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(obj_name, members))

        obj_name = "music/the_best_of_grok_and_drok/grok_live/vol_2/"
        self.assertIn(
            obj_name,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(obj_name, members))

        prefix = "music/the_best_of_grok_and_drok/grok_live/vol_1/"
        params = {"prefix": prefix, "delimiter": delimiter, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["subdir", "name"], response.content)

        expected = 3
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with prefix: {0} and delimiter: {1}"
            " expected: {2} members recieved: {3}".format(
                prefix,
                delimiter,
                expected,
                recieved))

        self.assertIn(
            vol1_obj1,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(vol1_obj1, members))

        self.assertIn(
            vol1_obj2,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(vol1_obj2, members))

        self.assertIn(
            vol1_obj3,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(vol1_obj3, members))

        prefix = "music/the_best_of_grok_and_drok/grok_live/vol_2/"
        params = {"prefix": prefix, "delimiter": delimiter, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["subdir", "name"], response.content)

        expected = 2
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with prefix: {0} and delimiter: {1}"
            " expected: {2} members recieved: {3}".format(
                prefix,
                delimiter,
                expected,
                recieved))

        self.assertIn(
            vol2_obj1,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(vol2_obj1, members))

        self.assertIn(
            vol2_obj2,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(vol2_obj2, members))

    def test_psuedo_dirs_with_path_query_parameter(self):
        """
        This is a depricated feature that has little documentation.
        The following things need to be done for the path parameter to work.
          1. For every "directory" a "directory marker" must be added as a
            object. The directory marker does not need to contain data, and
            thus can have a length of 0.
            Example:
            If you want a directory "foo/bar/", you would upload a object
            named "foo/bar/" to your container.

          2. You must upload your objects, prefixed with the "directory" path.
            Example:
            If you wanted to create an object in "foo/" and another in
            "foo/bar/", you would have to name the objects as follows:
                foo/object1.txt
                foo/bar/object2.txt

          3. Once this has been done, you can use the path query string
            parameter to list the objects in the simulated directory structure.
            Example:
            Using the above examples, setting path to "foo/" should list
            the following:
                foo/object1.txt
                foo/bar/
        """
        container_name = "{0}_{1}".format(
            CONTAINER_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(
            self.client.force_delete_containers,
            [container_name])

        """
        create dir markers
        """
        dir_marker_headers = {"Content-Length": "0"}

        lvl1_dir_marker = "level_1/"
        lvl2_dir_marker = "level_1/level_2/"
        lvl3_dir_marker = "level_1/level_2/level_3/"

        self.client.create_object(
            container_name,
            lvl1_dir_marker,
            headers=dir_marker_headers)

        self.client.create_object(
            container_name,
            lvl2_dir_marker,
            headers=dir_marker_headers)

        self.client.create_object(
            container_name,
            lvl3_dir_marker,
            headers=dir_marker_headers)

        """
        create objects
        """
        headers = {"Content-Length": str(len(self.default_obj_data)),
                   "Content-Type": CONTENT_TYPE_TEXT}

        """
        level 1 objects
        """
        lvl1_obj1 = "{0}{1}".format(lvl1_dir_marker, "lvl1_obj1")
        lvl1_obj2 = "{0}{1}".format(lvl1_dir_marker, "lvl1_obj2")

        self.client.create_object(
            container_name,
            lvl1_obj1,
            headers=headers,
            data=self.default_obj_data)

        self.client.create_object(
            container_name,
            lvl1_obj2,
            headers=headers,
            data=self.default_obj_data)

        """
        level 2 objects
        """
        lvl2_obj1 = "{0}{1}".format(lvl2_dir_marker, "lvl2_obj1")
        lvl2_obj2 = "{0}{1}".format(lvl2_dir_marker, "lvl2_obj2")

        self.client.create_object(
            container_name,
            lvl2_obj1,
            headers=headers,
            data=self.default_obj_data)

        self.client.create_object(
            container_name,
            lvl2_obj2,
            headers=headers,
            data=self.default_obj_data)

        """
        level 3 objects
        """
        lvl3_obj1 = "{0}{1}".format(lvl3_dir_marker, "lvl3_obj1")
        lvl3_obj2 = "{0}{1}".format(lvl3_dir_marker, "lvl3_obj2")

        self.client.create_object(
            container_name,
            lvl3_obj1,
            headers=headers,
            data=self.default_obj_data)

        self.client.create_object(
            container_name,
            lvl3_obj2,
            headers=headers,
            data=self.default_obj_data)

        """
        list objects
        """
        params = {"path": lvl1_dir_marker, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["name"], response.content)

        expected = 3
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with path: {0} expected: {1} members"
            " recieved: {2}".format(lvl1_dir_marker, expected, recieved))

        self.assertIn(
            lvl2_dir_marker,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl2_dir_marker, members))

        self.assertIn(
            lvl1_obj1,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl1_obj1, members))

        self.assertIn(
            lvl1_obj2,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl1_obj2, members))

        params = {"path": lvl2_dir_marker, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["name"], response.content)

        expected = 3
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with path: {0} expected: {1} members"
            " recieved: {2}".format(lvl3_dir_marker, expected, recieved))

        self.assertIn(
            lvl3_dir_marker,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl3_dir_marker, members))

        self.assertIn(
            lvl2_obj1,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl2_obj1, members))

        self.assertIn(
            lvl2_obj2,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl2_obj2, members))

        params = {"path": lvl3_dir_marker, "format": "json"}
        response = self.client.list_objects(container_name, params=params)

        members = self.get_members(["name"], response.content)

        expected = 2
        recieved = len(members)
        self.assertEqual(
            expected,
            recieved,
            msg="container list with path: {0} expected: {1} members"
            " recieved: {2}".format(lvl1_dir_marker, expected, recieved))

        self.assertIn(
            lvl3_obj1,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl3_obj1, members))

        self.assertIn(
            lvl3_obj2,
            members,
            msg="object name: {0} was not found in response body:"
            " {1}".format(lvl3_obj2, members))
