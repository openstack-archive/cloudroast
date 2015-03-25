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


class JsonSchemaOperationsSmoke(ImagesFixture):

    def test_get_images_schema(self):
        """
        @summary: Get images json schema

        1) Get images json schema
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_images_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_get_image_schema(self):
        """
        @summary: Get image json schema

        1) Get image json schema
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_image_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_get_image_members_schema(self):
        """
        @summary: Get image members json schema

        1) Get image members json schema
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_image_members_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_get_image_member_schema(self):
        """
        @summary: Get image member json schema

        1) Get image member json schema
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_image_member_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_get_tasks_schema(self):
        """
        @summary: Get tasks json schema

        1) Get tasks json schema
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_tasks_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_get_task_schema(self):
        """
        @summary: Get task json schema

        1) Get task json schema
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_task_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
