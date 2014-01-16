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
from cloudcafe.images.common.types import (
    ImageMemberStatus, TaskStatus, TaskTypes)
from cloudroast.images.fixtures import ObjectStorageIntegrationFixture


class TestShareImportedImage(ObjectStorageIntegrationFixture):

    @tags(type='positive', regression='true')
    def test_share_imported_image(self):
        """
        @summary: Share imported image

        1) As user A, create import task with a bootable image
        2) As user A, from the successful import task, get image
        3) Verify that the response code is 200
        4) Verify that the response contains the correct properties
        5) As user A, add image member (user B) to image id, effectively
        sharing the image with user B
        6) Verify that the response code is 200
        7) Verify that the response contains the correct properties
        8) As user B, accept the image
        9) Verify that the response code is 200
        10) As user B, list images
        11) Verify that the image is returned
        12) As user B, create a new server using the shared imported image
        13) Verify that the server goes to active status
        14) As user B, create a snapshot of the snapshot
        15) As user B, create export task using the snapshot
        16) Verify that the response code is 201
        17) Wait for the task to complete successfully
        18) List files in user B's container
        19) Verify that the response code is 200
        20) Verify that only one image with the image name exists
        """

        member_id = self.alt_tenant_id
        exported_images = []
        input_ = {'image_properties': {},
                  'import_from': self.import_from_bootable,
                  'import_from_format': self.import_from_format}

        task = self.images_behavior.create_new_task(input_=input_)
        image_id = task.result.image_id

        response = self.images_client.get_image(image_id)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity

        errors = self.images_behavior.validate_image(get_image)
        self.assertEqual(errors, [])

        response = self.images_client.add_member(image_id, member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity

        errors = self.images_behavior.validate_image_member(
            image_id, member, member_id)
        self.assertEqual(errors, [])

        response = self.alt_images_client.update_member(
            image_id, member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertIn(get_image, images)

        response = self.alt_server_behaviors.create_active_server(
            image_ref=image_id)
        self.assertEqual(response.status_code, 200)
        server = response.entity
        self.assertEqual(server.status.lower(), 'active')

        response = self.alt_compute_image_behaviors.create_active_image(
            server.id)
        image = response.entity

        input_ = {'image_uuid': image.id,
                  'receiving_swift_container': self.export_to}

        response = self.alt_images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.alt_images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        response = self.alt_object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        files = response.entity

        errors, file_names = self.alt_images_behavior.validate_exported_files(
            export_to=self.export_to, expect_success=True, files=files,
            image_id=image.id)
        self.assertListEqual(errors, [])
        for name in file_names:
            if name == '{0}.vhd'.format(image.id):
                exported_images.append(name)
        self.assertEqual(len(exported_images), 1)

    @tags(type='negative', regression='true')
    def test_attempt_to_export_shared_imported_image(self):
        """
        @summary: Attempt to export a shared imported image

        1) As user A, create import task
        2) As user A, add image member (user B) to image id, effectively
        sharing the image with user B
        3) Verify that the response code is 200
        4) As user B, attempt to export the image
        5) Verify that the export fails
        6) As user B, accept the image
        7) Verify that the response code is 200
        8) As user B, list images
        9) Verify that the image is returned
        10) List images owned by user B
        11) Verify that the image is not listed in the returned list
        12) As user B, attempt to export the image
        13) Verify that the export fails
        14) As user B, reject the image
        15) Verify that the response code is 200
        16) As user B, list images
        17) Verify that the image is not returned
        18) As user B, attempt to export the image
        19) Verify that the export fails
        20) Verify that the image does not appear in user B's container
        """

        member_id = self.alt_tenant_id

        task = self.images_behavior.create_new_task()
        image_id = task.result.image_id

        response = self.images_client.get_image(image_id)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity

        response = self.images_client.add_member(image_id, member_id)
        self.assertEqual(response.status_code, 200)

        input_ = {'image_uuid': image_id,
                  'receiving_swift_container': self.export_to}
        self._attempt_export_image(image_id, input_)

        response = self.alt_images_client.update_member(
            image_id, member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertIn(get_image, images)

        member_owned_images = self.alt_images_behavior.list_images_pagination(
            owner=member_id)
        self.assertNotIn(get_image, member_owned_images)

        self._attempt_export_image(image_id, input_)

        response = self.alt_images_client.update_member(
            image_id, member_id, ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(get_image, images)

        self._attempt_export_image(image_id, input_)

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        exported_image_names = [obj.name for obj in objects]
        self.assertNotIn('{0}.vhd'.format(image_id), exported_image_names)

    def _attempt_export_image(self, image_id, input_):
        """@summary: Attempt to export a given shared image"""

        response = self.alt_images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.alt_images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(task.message, Messages.NOT_OWNER_MSG)
