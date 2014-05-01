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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.constants import Messages
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestCreateImportTaskNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_create_import_task_with_extra_image_properties(self):
        """
        @summary: Create import task with extra image properties

        1) Create import task with extra image properties, name is the only
            allowed image property for an import task
        2) Verify that the response code is 201
        3) Wait for the task to fail
        4) Verify that the failed task contains the correct message
        """

        input_ = {'image_properties':
                  {'name': 'test_img', 'image_type': 'import'},
                  'import_from': self.import_from}
        error_msg = Messages.EXTRA_IMAGE_PROPERTIES_MSG

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(task.message, error_msg)
