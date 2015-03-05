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

from cloudroast.glance.fixtures import ImagesFixture


class DeleteTask(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteTask, cls).setUpClass()

        cls.created_task = cls.images.behaviors.create_new_task()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(DeleteTask, cls).tearDownClass()

    def test_delete_task(self):
        """
        @summary: Delete a task

        1) Delete a task passing in a task id
        2) Verify the response status code is 405
        3) Get task details
        4) Verify that the response is ok
        5) Verify that the returned task's properties are as expected
        generically
        """

        resp = self.images.client.delete_task(self.created_task.id_)
        self.assertEqual(resp.status_code, 405,
                         self.status_code_msg.format(405, resp.status_code))

        resp = self.images.client.get_task_details(self.created_task.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_task_details = resp.entity

        errors = self.images.behaviors.validate_task(get_task_details)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))
