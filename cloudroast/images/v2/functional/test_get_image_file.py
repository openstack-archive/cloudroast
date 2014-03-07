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
from cloudcafe.images.common.types import ImageMemberStatus, TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestGetImageFile(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_get_image_file(self):
        """
        @summary: Get image file

        1) Create new image containing data file
        2) Get image file
        3) Verify that the response code is 200
        4) Verify that the image file contains the correct data
        """

        file_data = self.test_file

        image = self.images_behavior.create_new_image()

        response = self.images_client.store_image_file(image.id_, file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image_file(image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, file_data)

    @tags(type='positive', regression='true')
    def test_get_image_file_as_a_member_of_the_image(self):
        """
        @summary: Get image file as a member of the image

        1. Create image as tenant
        2. Store image file as tenant
        3. Verify that the response code is 204
        4. Add alternative tenant as a member of the image
        5. Verify that alternative tenant belongs to image members list
        6. Get image file as alternative tenant
        7. Verify that the response code is 200
        8. Verify that the response content is the same as image data
        """

        alt_tenant_id = self.alt_tenant_id
        file_data = self.test_file
        image = self.images_behavior.create_new_image()
        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.add_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        members_ids = self.images_behavior.get_member_ids(image_id=image.id_)
        self.assertIn(alt_tenant_id, members_ids)

        response = self.alt_images_client.get_image_file(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.image_data)

    @tags(type='positive', regression='true')
    def test_verify_object_and_imported_exported_image_content(self):
        """
        @summary: Verify that an imported image's content is same as the file
        object's content in the customer's container and the exported image's
        content

        1) Get the import file object's content
        2) Verify that the response code is 200
        3) Create new image
        4) Get the new image's file content
        5) Verify that the response code is 200
        6) Verify that the import file object's content is the same data as as
        the image's file content
        7) Export the image
        8) Get the exported file object's content
        9) Verify that the response code is 200
        10) Verify that the export file object's content is the same data as as
        the image's file content
        11) Verify that the import file object's content is the same data as as
        the export file object's content
        """

        response = self.object_storage_client.get_object(
            container_name='test_container', object_name='import_test.vhd')
        self.assertEqual(response.status_code, 200)
        file_content = response.content

        task = self.images_behavior.create_new_task()
        image_id = task.result.image_id

        response = self.images_client.get_image_file(image_id)
        self.assertEqual(response.status_code, 200)
        image_content = response.content

        self.assertEqual(file_content, image_content)

        input_ = {'image_uuid': image_id,
                  'receiving_swift_container': self.export_to}

        task = self.images_behavior.create_new_task(
            input_=input_, type_=TaskTypes.EXPORT)

        export_location = [
            x.strip() for x in task.result.export_location.split('/')]
        response = self.object_storage_client.get_object(
            container_name=export_location[0], object_name=export_location[1])
        self.assertEqual(response.status_code, 200)
        new_file_content = response.content

        self.assertEqual(new_file_content, image_content)
        self.assertEqual(file_content, new_file_content)
