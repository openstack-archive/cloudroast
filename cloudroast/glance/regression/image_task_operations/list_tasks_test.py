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
from cloudcafe.glance.common.types import TaskTypes

from cloudroast.glance.fixtures import ImagesFixture


class ListTasks(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ListTasks, cls).setUpClass()

        cls.created_task = cls.images.behaviors.create_new_task()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ListTasks, cls).tearDownClass()

    def test_list_tasks(self):
        """
        @summary: List tasks and verify that the created task is present

        1) List tasks
        2) Verify that the response code is 200
        3) Verify that the list is not empty
        4) Verify that the created task is in the list of tasks
        5) Verify that each returned tasks has the expected properties
        """

        returned_task_ids = []
        errors = []

        resp = self.images.client.list_tasks()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        listed_tasks = resp.entity

        self.assertNotEqual(
            len(listed_tasks), 0,
            msg=('Unexpected number of tasks received. Expected: Not 0 '
                 'Received: {0}').format(len(listed_tasks)))

        [returned_task_ids.append(task.id_) for task in listed_tasks
         if task.id_ == self.created_task.id_]

        self.assertEqual(
            len(returned_task_ids), 1,
            msg=('Unexpected number of tasks received. Expected: 1 '
                 'Received: {0}').format(len(returned_task_ids)))

        for task in listed_tasks:
            if task.input_ is not None:
                errors.append(Messages.PROPERTY_MSG.format(
                    'input', 'None', task.input_))
            if task.result is not None:
                errors.append(Messages.PROPERTY_MSG.format(
                    'result', 'None', task.result))
            if task.owner != self.images.auth.tenant_id:
                errors.append(Messages.PROPERTY_MSG.format(
                    'owner', self.images.auth.tenant_id, task.owner))

        self.assertEqual(
            errors, [],
            msg=('Unexpected errors received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_list_tasks_filter_type(self):
        """
        @summary: List tasks passing filter type as import

        1) List tasks passing the filter type as import
        2) Verify that the response code is 200
        3) Verify that the list is not empty
        3) Verify that the owner of each listed task belongs to the user
        performing the request
        4) Verify that the type of each listed task is import
        """

        errors = []

        resp = self.images.client.list_tasks(params={'type': TaskTypes.IMPORT})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        listed_tasks = resp.entity

        self.assertNotEqual(
            len(listed_tasks), 0,
            msg=('Unexpected number of tasks received. Expected: Not 0 '
                 'Received: {0}').format(len(listed_tasks)))

        for task in listed_tasks:
            if task.owner != self.images.auth.tenant_id:
                errors.append(Messages.PROPERTY_MSG.format(
                    'owner', self.images.auth.tenant_id, task.owner))
            if task.type_ is TaskTypes.IMPORT:
                errors.append(self.error_msg.format(
                    'type_', TaskTypes.IMPORT, task.type_))

        self.assertEqual(
            errors, [],
            msg=('Unexpected errors received. Expected: No errors '
                 'Received: {0}').format(errors))
