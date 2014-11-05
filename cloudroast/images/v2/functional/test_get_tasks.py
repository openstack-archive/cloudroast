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
from cloudcafe.images.common.types import TaskTypes

from cloudroast.images.fixtures import ImagesFixture


class TestGetTasks(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetTasks, cls).setUpClass()
        cls.tasks = cls.images_behavior.create_new_tasks(count=2)

    @tags(type='smoke')
    def test_get_tasks(self):
        """
        @summary: Get tasks

        1) Get tasks
        2) Verify that the response code is 200
        3) Verify that the list is not empty
        4) Verify that the owner of each listed task belongs to the user
        performing the request and that the data is correct
        """

        response = self.images_client.list_tasks()
        self.assertEqual(response.status_code, 200)

        get_tasks = response.entity
        self.assertNotEqual(len(get_tasks), 0)

        [self._validate_listed_task(task) for task in get_tasks]

    @tags(type='positive', regression='true')
    def test_get_tasks_pagination(self):
        """
        @summary: Get all tasks by paginating through all results and verify
        that the created images are present

        1) Given two created tasks, get tasks
        2) Verify that the list is not empty
        3) Verify that the owner of each listed task belongs to the user
        performing the request and that the data is correct
        4) Verify that the created tasks are in the list of tasks
        """

        count = 2
        created_tasks = []
        first_task = self.tasks.pop()
        second_task = self.tasks.pop()

        get_tasks = self.images_behavior.list_tasks_pagination()
        self.assertNotEqual(len(get_tasks), 0)

        for task in get_tasks:
            self._validate_listed_task(task)
            if (task.id_ == first_task.id_ or task.id_ == second_task.id_):
                created_tasks.append(task)

        self.assertEqual(len(created_tasks), count)

    @tags(type='positive', regression='true')
    def test_get_tasks_filter_type(self):
        """
        @summary: Get tasks with a filter of type

        1) Given two created tasks, get tasks using the filter of 'type' set
        to 'import'
        2) Verify that the list is not empty
        3) Verify that the owner of each listed task belongs to the user
        performing the request
        4) Verify that the type of each listed task is 'import'
        """

        get_tasks = self.images_behavior.list_tasks_pagination(
            type_=TaskTypes.IMPORT)
        self.assertNotEqual(len(get_tasks), 0)

        for task in get_tasks:
            self.assertEqual(task.owner, self.tenant_id)
            self.assertEqual(task.type_, TaskTypes.IMPORT)

    def _validate_listed_task(self, task):
        """
        @summary: Validate that the listed task does not contain certain
        properties and that the owner is correct
        """

        errors = []

        if task.input_ is not None:
            errors.append(self.error_msg.format('input', 'None', task.input_))
        if task.result is not None:
            errors.append(self.error_msg.format('result', 'None', task.result))
        if task.owner != self.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.tenant_id, task.owner))

        self.assertListEqual(errors, [])
