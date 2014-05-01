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

from cafe.drivers.unittest.decorators import tags
from cloudroast.images.fixtures import ImagesFixture


class TestDeleteTask(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_delete_task(self):
        """
        @summary: Delete task

        1) Create task
        2) Delete task
        3) Verify that the response code is 405
        4) Verify that the response contains the allowed header
        """

        task = self.images_behavior.create_new_task()

        response = self.images_client.delete_task(task.id_)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers.get('allow'), "GET")
