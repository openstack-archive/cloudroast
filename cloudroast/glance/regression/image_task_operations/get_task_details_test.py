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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture


class GetTaskDetails(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(GetTaskDetails, cls).setUpClass()

        input_ = {'image_properties': {'name': rand_name('get_task')},
                  'import_from': cls.images.config.import_from}

        cls.created_task = cls.images.behaviors.create_new_task(input_)
        cls.task_created_at_time_in_sec = calendar.timegm(time.gmtime())

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(GetTaskDetails, cls).tearDownClass()

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
