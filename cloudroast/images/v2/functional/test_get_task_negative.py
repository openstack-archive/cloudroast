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


class TestGetTaskNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_get_task_not_owned_by_tenant(self):
        """
        @summary: Get task that is not owned by tenant

        1) Create task with alt_user
        2) Get task that is not owned by tenant
        3) Verify that the response code is 404
        """

        task = self.alt_images_behavior.create_new_task()

        response = self.images_client.get_task(task.id_)
        self.assertEqual(response.status_code, 404)
