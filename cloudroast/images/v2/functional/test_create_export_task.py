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

import calendar
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestCreateExportTask(ComputeIntegrationFixture):

#     @classmethod
#     def setUpClass(cls):
#         super(TestCreateExportTask, cls).setUpClass()
#         server = cls.server_behaviors.create_active_server().entity
#         image = cls.compute_image_behaviors.create_active_image(server.id)
#         cls.image = cls.images_client.get_image(image.entity.id).entity

    @tags(type='smoke', test='testtest')
    def test_create_export_task(self):
        """
        @summary: Create export task

        1) Given a previously created image, create export task
        2) Verify that the response code is 201
        3) Verify that the task properties are returned correctly
        """

#         data = self.images_behavior.create_data_file()

        input_ = {'image_uuid': self.image.id,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)

        task = response.entity

        errors = self.images_behavior.validate_task(task)

        self._validate_specific_task_properties(
            task, task_creation_time_in_sec)

        self.assertListEqual(errors, [])

    @tags(type='positive', regression='true', test='testtest')
    def test_attempt_duplicate_export_task(self):
        """
        @summary: Attempt to create a duplicate of the same import take

        1) Create import task
        2) Verify that the response code is 201
        3) Create another import take with the same input properties
        4) Verify that the response code is 201
        5) Verify that the first import task is not the same as the second
        import task
        """

        tasks = []
        input_ = {'image_uuid': self.image_id,
                  'receiving_swift_container': self.export_to}

        for i in range(2):
            response = self.images_client.create_task(
                input_=input_, type_=TaskTypes.EXPORT)
            self.assertEqual(response.status_code, 201)
            task_id = response.entity.id_
            task = self.images_behavior.wait_for_task_status(
                task_id, TaskStatus.SUCCESS)
            tasks.append(task)

        self.assertNotEqual(tasks[0], tasks[1])

    def _validate_specific_task_properties(self, task,
                                           task_creation_time_in_sec):
        """
        @summary: Validate that the created task contains the expected
        properties
        """

        errors = []

        get_created_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.created_at)
        get_updated_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.updated_at)

        if task.status != TaskStatus.PENDING:
            errors.append(self.error_msg.format(
                'status', TaskStatus.PENDING, task.status))
        if get_created_at_delta > self.max_created_at_delta:
            errors.append(self.error_msg.format(
                'created_at delta', self.max_created_at_delta,
                get_created_at_delta))
        if task.expires_at is not None:
            errors.append(self.error_msg.format(
                'expires_at', None, task.expires_at))
        if task.input_.image_properties != {}:
            errors.append(self.error_msg.format(
                'image_properties', 'not {}', task.input_.image_properties))
        if task.input_.import_from is None:
            errors.append(self.error_msg.format(
                'import_from', None, task.input_.import_from))
        if task.input_.import_from_format is None:
            errors.append(self.error_msg.format(
                'import_from_format', None, task.input_.import_from_format))
        if task.input_.image_uuid != self.image.id:
            errors.append(self.error_msg.format(
                'image_uuid', self.image.id, task.input_.image_uuid))
        if task.input_.receiving_swift_container != self.export_to:
            errors.append(self.error_msg.format(
                'receiving_swift_container', self.export_to,
                task.input_.receiving_swift_container))
        if get_updated_at_delta > self.max_updated_at_delta:
            errors.append(self.error_msg.format(
                'updated_at delta', self.max_updated_at_delta,
                get_updated_at_delta))
        if task.type_ != TaskTypes.EXPORT:
            errors.append(self.error_msg.format(
                'type_', TaskTypes.EXPORT, task.type_))
        if task.result is not None:
            errors.append(self.error_msg.format('result', None, task.result))
        if task.owner != self.user_config.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.user_config.tenant_id, task.owner))

        self.assertListEqual(errors, [])
