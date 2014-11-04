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
from cloudcafe.compute.common.exceptions import BadMethod
from cloudcafe.images.common.types import TaskTypes

from cloudroast.images.fixtures import ImagesFixture


class TestDeleteTask(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestDeleteTask, cls).setUpClass()
        cls.task = cls.images_behavior.create_new_task()

    @tags(type='positive', regression='true')
    def test_delete_task(self):
        """
        @summary: Delete task

        1) Given a previously created task, delete the task
        3) Verify that the response code is 405
        4) List tasks and verify the task tried to delete is still present
        """

        with self.assertRaises(BadMethod):
            self.images_client.delete_task(self.task.id_)

        get_tasks = self.images_behavior.list_tasks_pagination(
            type_=TaskTypes.IMPORT)

        self.assertTrue(any([task for task in get_tasks
                             if task.id_ == self.task.id_]))
