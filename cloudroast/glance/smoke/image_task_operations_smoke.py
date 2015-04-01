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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import TaskTypes

from cloudroast.glance.fixtures import ImagesFixture


class ImageTaskOperationsSmoke(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageTaskOperationsSmoke, cls).setUpClass()

        import_from = cls.images.config.import_from
        input_ = {'image_properties':
                  {'name': rand_name('image_task_operations_smoke')},
                  'import_from': import_from}

        # Count set to number of tasks required for this module
        created_tasks = cls.images.behaviors.create_new_tasks(input_, count=2)

        cls.created_task = created_tasks.pop()
        cls.alt_created_task = created_tasks.pop()

        cls.created_image = cls.images.behaviors.create_image_via_task(
            image_properties={'name':
                              rand_name('image_task_operations_smoke')})

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageTaskOperationsSmoke, cls).tearDownClass()

    def test_list_tasks(self):
        """
        @summary: List subset of tasks

        1) List subset of tasks
        2) Verify the response status code is 200
        """

        resp = self.images.client.list_tasks()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_get_task_details(self):
        """
        @summary: Get the details of a task

        1) Get the details of a task passing in a task id
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_task_details(self.created_task.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_task_to_import_image(self):
        """
        @summary: Create a task to import an image

        1) Create a task to import an image passing in an input containing the
        image properties and location to import the image from
        2) Verify the response status code is 201
        """

        input_ = {'image_properties':
                  {'name': rand_name('image_task_operations_smoke')},
                  'import_from': self.images.config.import_from}

        resp = self.images.client.task_to_import_image(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))

    def test_task_to_export_image(self):
        """
        @summary: Create a task to export an image

        1) Create a task to export an image passing in an input containing the
        image id and location to export the image to
        2) Verify the response status code is 201
        """

        input_ = {'image_uuid': self.created_image.id_,
                  'receiving_swift_container': self.images.config.export_to}

        resp = self.images.client.task_to_export_image(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))

    def test_delete_task(self):
        """
        @summary: Delete a task

        1) Delete a task passing in a task id
        2) Verify the response status code is 405
        """

        resp = self.images.client.delete_task(self.alt_created_task.id_)
        self.assertEqual(
            resp.status_code, 405,
            Messages.STATUS_CODE_MSG.format(405, resp.status_code))
