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

CONTENT_TYPE_TEXT = "text/plain; charset=UTF-8"
CONTAINER_NAME = 'list_delimiter_test_container'


class DelimiterTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(DelimiterTest, cls).setUpClass()

        cls.container_name = CONTAINER_NAME
        cls.client.create_container(cls.container_name)

        cls.object_data = Constants.VALID_OBJECT_DATA
        cls.content_length = str(len(cls.object_data))
        cls.headers = {"Content-Length": cls.content_length,
                       "Content-Type": CONTENT_TYPE_TEXT}

    @classmethod
    def tearDownClass(cls):
        super(DelimiterTest, cls).setUpClass()
        cls.behaviors.force_delete_containers([cls.container_name])

    def test_delimeter(self):
        """
        Scenario: create three objs and perform a container list using
        the 'delimiter' query string parameter

        Expected Results: return all of the top level psuedo directories
        and objects in a container. if the object name is 'foo/bar'
        then the top level psuedo dir name would be 'foo/'
        """
        obj_names = ["asteroid_photo",
                     "music_collection0/grok_n_roll/grok_against_the_machine",
                     "music_to_sling_code_to",
                     "music_collection2/maximum_drok",
                     "transparent_aluminum_doc"]

        for obj_name in obj_names:
            self.client.create_object(
                self.container_name,
                obj_name,
                headers=self.headers,
                data=self.object_data)

        params = {"delimiter": "/", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        parsed_content = []
        for member in content:
            if "subdir" in member.keys():
                parsed_content.append(member["subdir"])
            elif "name" in member.keys():
                parsed_content.append(member["name"])
            else:
                continue

        expected = len(obj_names)
        recieved = len(parsed_content)

        self.assertEqual(
            expected,
            recieved,
            msg="expected {0} objects in the response body, recieved"
                " {1}".format(expected, recieved))

        for obj_name in obj_names:
            tokens = obj_name.split('/')
            if len(tokens) > 1:
                # top level psuedo dir
                current_name = "{0}/".format(tokens[0])
            else:
                # object name
                current_name = tokens[0]

            self.assertIn(current_name, parsed_content)
