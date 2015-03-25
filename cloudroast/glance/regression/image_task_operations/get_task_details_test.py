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

import calendar
import time

from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import TaskStatus

from cloudroast.glance.fixtures import ImagesFixture


class GetTaskDetails(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(GetTaskDetails, cls).setUpClass()

        cls.created_task = cls.images.behaviors.create_new_task()
        cls.task_created_at_time_in_sec = calendar.timegm(time.gmtime())

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(GetTaskDetails, cls).tearDownClass()

    def test_get_task_details(self):
        """
        @summary: Get task details

        1) Get task details of created task
        2) Verify that the response code is 200
        3) Verify that the returned task's properties are as expected
        generically
        4) Verify that the returned task's properties are as expected more
        specifically
        """

        resp = self.images.client.get_task_details(self.created_task.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_task_details = resp.entity

        errors = self.images.behaviors.validate_task(get_task_details)

        created_at_delta = self.images.behaviors.get_time_delta(
            self.task_created_at_time_in_sec, get_task_details.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            self.task_created_at_time_in_sec, get_task_details.updated_at)
        expires_at_delta = self.images.behaviors.get_time_delta(
            self.task_created_at_time_in_sec, get_task_details.expires_at)

        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if expires_at_delta > self.images.config.max_expires_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'expires_at delta', self.images.config.max_expires_at_delta,
                expires_at_delta))
        if get_task_details.owner != self.images.auth.tenant_id:
                errors.append(Messages.PROPERTY_MSG.format(
                    'owner', self.images.auth.tenant_id,
                    get_task_details.owner))
        if get_task_details.status != TaskStatus.SUCCESS:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', TaskStatus.SUCCESS, get_task_details.status))
        if updated_at_delta > self.images.config.max_updated_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at delta', self.images.config.max_updated_at_delta,
                updated_at_delta))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_get_task_details_as_tenant_without_access_to_task(self):
        """
        @summary: Get task details of a task as a tenant that does not have
        access to the task

        1) Get task details of task that is not owned by tenant
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.get_task_details(
            self.created_task.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

        self.assertIsNone(
            resp.entity, msg=('Unexpected task returned. Expected: None '
                              'Received: {0}').format(resp.entity))

    def test_get_task_details_using_blank_task_id(self):
        """
        @summary: Get task details using a blank task id

        1) Get task details using a blank task id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_task_details(task_id='')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_get_task_details_using_invalid_task_id(self):
        """
        @summary: Get task details using a invalid task id

        1) Get task details using a invalid task id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_task_details(task_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))
