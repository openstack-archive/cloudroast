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
from cloudcafe.images.common.types import (
    ImageMemberStatus, TaskStatus, TaskTypes)
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestShareImportedImage(ComputeIntegrationFixture):

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
        """

        member_id = self.alt_tenant_id
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

    @unittest.skip('Bug, Redmine #4721')
    @tags(type='negative', regression='true', test='test')
    def test_attempt_to_export_shared_imported_image(self):
        """
        @summary: Attempt to export a shared imported image

        1) As user A, create import task
        2) As user A, add image member (user B) to image id, effectively
        sharing the image with user B
        3) Verify that the response code is 200
        4) As user B, accept the image
        5) Verify that the response code is 200
        6) As user B, list images
        7) Verify that the image is returned
        8) List images owned by user B
        9) Verify that the image is not listed in the returned list
        10) As user B, attempt to export the image
        11) Verify that the export fails
        12) Verify that the image does not appear in user B's container
        """

        member_id = self.alt_tenant_id

        task = self.images_behavior.create_new_task()
        image_id = task.result.image_id

        response = self.images_client.get_image(image_id)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity

        response = self.images_client.add_member(image_id, member_id)
        self.assertEqual(response.status_code, 200)

        response = self.alt_images_client.update_member(
            image_id, member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertIn(get_image, images)

        member_owned_images = self.alt_images_behavior.list_images_pagination(
            owner=member_id)
        self.assertNotIn(get_image, member_owned_images)

        input_ = {'image_uuid': image_id,
                  'receiving_swift_container': self.export_to}
        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(
            task.message, '{0}{1}'.format(image_id, self.export_to))

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        exported_image_names = [obj.name for obj in objects]
        self.assertNotIn(image_id, exported_image_names)
