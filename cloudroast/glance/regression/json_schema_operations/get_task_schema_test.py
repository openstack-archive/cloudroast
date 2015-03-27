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

from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture


class GetTaskSchema(ImagesFixture):

    def test_get_task_schema(self):
        """
        @summary: Get task json schema

        1) Retrieve the task schema json resp file
        2) Get task json schema
        3) Verify the response status code is 200
        4) Verify that the response body contain the expected task schema as
        compared to the task schema json file
        """

        with open(self.images.config.task_schema_json, 'r') as DATA:
            task_schema_resp = DATA.read().rstrip()

        resp = self.images.client.get_task_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        self.assertEqual(resp.content, task_schema_resp)
