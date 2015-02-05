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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class ImageSharingOperationsSmoke(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageSharingOperationsSmoke, cls).setUpClass()
        cls.member_id = cls.images_alt_one.auth.tenant_id
        cls.created_images = cls.images.behaviors.create_images_via_task(
            count=5)
        cls.image = cls.created_images.pop()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageSharingOperationsSmoke, cls).tearDownClass()

    @data_driven_test(ImagesDatasetListGenerator.ListImageMembers())
    def ddtest_list_image_members(self, params):
        """
        @summary: List all image members

        @param params: Parameter being passed to the list image members request
        @type params: Dictionary

        1) List all image members passing in a query parameter
        2) Verify the response status code is 200
        """

        resp = self.images.client.list_image_members(self.image.id_, params)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

    def test_get_image_member(self):
        """
        @summary: Get an image member of an image

        1) As user A, create an image member for an image passing the image id
        and user B's tenant id as member id
        2) Verify the response status code is 200
        3) As user A, get an image member of an image passing in the image id
        and member id
        4) Verify the response status code is 200
        """

        image = self.created_images.pop()

        resp = self.images.client.create_image_member(
            image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

        resp = self.images.client.get_image_member(image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

    def test_create_image_member(self):
        """
        @summary: Create an image member

        1) As user A, create an image member for an image passing the image id
        and user B's tenant id as member id
        2) Verify the response status code is 200
        """

        image = self.created_images.pop()

        resp = self.images.client.create_image_member(
            image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

    def test_delete_image_member(self):
        """
        @summary: Delete an image member

        1) As user A, create an image member for an image passing the image id
        and user B's tenant id as member id
        2) Verify the response status code is 200
        """

        image = self.created_images.pop()

        resp = self.images.client.create_image_member(
            image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

        resp = self.images.client.delete_image_member(
            image.id_, self.member_id)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

    def test_update_image_member(self):
        """
        @summary: Update an image member

        1) As user A, create an image member for an image passing the image id
        and user B's tenant id as member id
        2) Verify the response status code is 200
        3) As user B, update an image member of an image passing in the
        image id, member id, and 'accepted' as the status
        4) Verify the response status code is 200
        """

        image = self.created_images.pop()

        resp = self.images.client.create_image_member(
            image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

        resp = self.images_alt_one.client.update_image_member(
            image.id_, self.member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
