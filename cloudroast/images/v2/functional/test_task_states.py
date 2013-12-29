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
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestTaskStates(ImagesFixture):

    @tags(type='positive', regression='true')
    @unittest.skip('Bug, Redmine #4226')
    def test_import_task_states(self):
        """
        @summary: Import task states - pending, processing, success

        1) Create task
        2) Verify that the response code is 201
        3) Verify that the status is 'pending'
        4) Get task, verify that the status changes from 'pending' to
        'processing'
        5) Get task, verify that the status changes from 'processing' to
        'success'
        6) Verify that the task's properties appear correctly
        7) Verify that a result property with image_id is returned
        8) Verify that a message property is not returned
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)

        task = response.entity

        self.assertEqual(task.status, TaskStatus.PENDING)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.PROCESSING)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.SUCCESS)

        errors = self.images_behavior.validate_task(task)
        if self.id_regex.match(task.result.image_id) is None:
            errors.append(self.error_msg.format(
                'image_id', not None,
                self.id_regex.match(task.result.image_id)))
        if task.message is not None:
            errors.append(self.error_msg.format(
                'message', None, task.message))

        self.assertListEqual(errors, [])
