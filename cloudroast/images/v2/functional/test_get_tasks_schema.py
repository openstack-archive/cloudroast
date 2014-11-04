"""
Copyright 2014 Rackspace

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

from cafe.drivers.unittest.decorators import tags

from cloudroast.images.fixtures import ImagesFixture


class TestGetTasksSchema(ImagesFixture):

    @tags(type='smoke')
    def test_get_tasks_schema(self):
        """
        @summary: Get schema that represents an tasks entity

        1) Get tasks schema
        2) Verify that the response status code is 200
        3) Verify that the response body contain the expected tasks schema as
        compared to the tasks_schema.json file
        """

        tasks_schema_json = self.read_data_file(
            self.images_config.tasks_schema_json)

        response = self.images_client.get_tasks_schema()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, tasks_schema_json)
