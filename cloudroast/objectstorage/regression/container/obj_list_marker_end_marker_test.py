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

from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
CONTAINER_NAME = 'list_marker_test_container'


class MarkerEndMarkerTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(MarkerEndMarkerTest, cls).setUpClass()

        cls.container_name = CONTAINER_NAME
        cls.client.create_container(cls.container_name)

        object_data = Constants.VALID_OBJECT_DATA
        content_length = str(len(object_data))
        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        cls.obj_names = ["b_obj", "c_obj", "d_obj", "e_obj", "f_obj", "g_obj"]

        for obj_name in cls.obj_names:
            cls.client.create_object(
                cls.container_name,
                obj_name,
                headers=headers,
                data=object_data)

    @classmethod
    def tearDownClass(cls):
        super(MarkerEndMarkerTest, cls).setUpClass()
        cls.behaviors.force_delete_containers([cls.container_name])

    def test_marker(self):
        params = {"marker": "c", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = 5
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertIn("c_obj", members, msg="c_obj was not in the response")
        self.assertIn("d_obj", members, msg="d_obj was not in the response")
        self.assertIn("e_obj", members, msg="e_obj was not in the response")
        self.assertIn("f_obj", members, msg="f_obj was not in the response")
        self.assertIn("g_obj", members, msg="g_obj was not in the response")

    def test_marker_lower_bound(self):
        params = {"marker": "a", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = len(self.obj_names)
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertEqual(
            members,
            self.obj_names,
            msg="expected {0} recieved {1}".format(members, self.obj_names))

    def test_marker_swapped_lower_bound(self):
        params = {"marker": "h", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        self.assertTrue(response.ok)

        expected = 0
        recieved = len(content)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))

    def test_end_marker(self):
        params = {"end_marker": "d", "format": "json", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
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
        self.assertIn("b_obj", members, msg="b_obj was not in the response")
        self.assertIn("c_obj", members, msg="c_obj was not in the response")

    def test_end_marker_upper_bound(self):
        params = {"end_marker": "h", "format": "json", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = len(self.obj_names)
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertEqual(
            members,
            self.obj_names,
            msg="expected {0} recieved {1}".format(members, self.obj_names))

    def test_end_marker_swapped_uppper_bound(self):
        params = {"end_marker": "a", "format": "json", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        self.assertTrue(response.ok)

        expected = 0
        recieved = len(content)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))

    def test_marker_end_marker(self):
        params = {"marker": "b", "end_marker": "e", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = 3
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertIn("b_obj", members, msg="b_obj was not in the response")
        self.assertIn("c_obj", members, msg="c_obj was not in the response")
        self.assertIn('d_obj', members, msg="d_obj was not in the response")

    def test_marker_end_marker_lower_upper_bound(self):
        params = {"marker": "a", "end_marker": "h", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = len(self.obj_names)
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertEqual(
            members,
            self.obj_names,
            msg="expected {0} recieved {1}".format(members, self.obj_names))

    def test_marker_end_marker_swapped_upper_lower_bound(self):
        params = {"marker": "h", "end_marker": "a", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        self.assertTrue(response.ok)

        expected = 0
        recieved = len(content)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))

    def test_marker_limit(self):
        params = {"marker": "b", "limit": "2", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
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
        self.assertIn("b_obj", members, msg="b_obj was not in the response")
        self.assertIn("c_obj", members, msg="c_obj was not in the response")

    def test_marker_limit_lower_bound(self):
        params = {"marker": "a", "limit": "6", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = len(self.obj_names)
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertEqual(
            members,
            self.obj_names,
            msg="expected {0} recieved {1}".format(members, self.obj_names))

    def test_marker_limit_swapped_lower_bound(self):
        params = {"marker": "h", "limit": "6", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        self.assertTrue(response.ok)

        expected = 0
        recieved = len(content)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))

    def test_end_marker_limit(self):
        params = {"end_marker": "e", "limit": "2", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
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
        self.assertIn("b_obj", members, msg="b_obj was not in the response")
        self.assertIn("c_obj", members, msg="c_obj was not in the response")

    def test_end_marker_limit_upper_bound(self):
        params = {"end_marker": "h", "limit": "6", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = len(self.obj_names)
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertEqual(
            members,
            self.obj_names,
            msg="expected {0} recieved {1}".format(members, self.obj_names))

    def test_end_marker_limit_swapped_upper_bound(self):
        params = {"end_marker": "a", "limit": "6", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        self.assertTrue(response.ok)

        expected = 0
        recieved = len(content)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))

    def test_marker_end_marker_limit(self):
        params = {"marker": "b",
                  "end_marker": "e",
                  "limit": "2",
                  "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
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
        self.assertIn("b_obj", members, msg="b_obj was not in the response")
        self.assertIn("c_obj", members, msg="c_obj was not in the response")

    def test_marker_end_marker_limit_upper_lower_bound(self):
        params = {"marker": "a",
                  "end_marker": "h",
                  "limit": "6",
                  "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        members = []
        for member in content:
            if 'name' in member:
                members.append(member['name'])
            else:
                continue

        self.assertTrue(response.ok)

        expected = len(self.obj_names)
        recieved = len(members)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
        self.assertEqual(
            members,
            self.obj_names,
            msg="expected {0} recieved {1}".format(members, self.obj_names))

    def test_marker_end_marker_limit_swapped_upper_lower_bound(self):
        params = {"marker": "h",
                  "end_marker": "a",
                  "limit": "6",
                  "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        self.assertTrue(response.ok)

        expected = 0
        recieved = len(content)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} members in the response, recieved {1}".format(
                expected,
                recieved))
