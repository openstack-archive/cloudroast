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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestGetTasks(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetTasks, cls).setUpClass()
        cls.tasks = cls.images_behavior.create_new_tasks(count=4)

    @tags(type='smoke')
    def test_get_tasks(self):
        """
        @summary: Get tasks

        1) Given two created tasks, get tasks
        2) Verify that the list is not empty
        3) Verify that the owner of each listed task belongs to the user
        performing the request
        4) Verify that the created tasks are in the list of tasks
        """

        count = 2
        created_tasks = []
        first_task = self.tasks.pop()
        second_task = self.tasks.pop()

        get_tasks = self.images_behavior.list_tasks_pagination()
        self.assertNotEqual(len(get_tasks), 0)

        for task in get_tasks:
            self.assertEqual(task.owner, self.tenant_id)
            if (task.id_ == first_task.id_ or task.id_ == second_task.id_):
                created_tasks.append(task)

        self.assertEqual(len(created_tasks), count)

    @unittest.skip('Bug, Redmine #4727')
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
