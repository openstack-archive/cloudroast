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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class UpdateImageNegativeTest(ImagesFixture):
    @classmethod
    def setUpClass(cls):
        super(UpdateImageNegativeTest, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image()

    @classmethod
    def tearDownClass(cls):
        super(UpdateImageNegativeTest, cls).tearDownClass()

    @tags(type='negative', regression='true')
    def test_update_image_with_invalid_visibility(self):
        """
        @summary: Try to update an image's visibility with invalid visibility.

        1. Create an image
        2. Update image's visibility with invalid visibility
        3. Verify response code is 400
        """

        updated_image_visibility = rand_name("invalid_visibility")

        response = self.images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        response = self.images_client.update_image(
            image_id=self.image.id_,
            replace={"visibility": updated_image_visibility})
        self.assertEqual(response.status_code, 400)

    @tags(type='negative', regression='true')
    def test_update_image_add_status(self):
        """
        @summary: Try to update an image by adding status property to it.

        1. Create an image
        2. Update image's status by adding new status property to it
        3. Verify response code is 403
        """

        response = self.images_client.update_image(
            image_id=self.image.id_, add={"status": rand_name("status-")})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_remove_status(self):
        """
        @summary: Try to remove the status property from an image.

        1. Create an image
        2. Update image's status, by removing it.
        3. Verify the response code is 403
        """

        response = self.images_client.update_image(
            image_id=self.image.id_, remove={"status": rand_name("remove")})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_replace_status(self):
        """
        @summary: Try to replace the status property of an image.

        1. Create an image
        2. Update image's status, by replacing it.
        3. Verify the response code is 403
        """

        response = self.images_client.update_image(
            image_id=self.image.id_, replace={"status": rand_name("replace")})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_using_http_method_put(self):
        """
        @summary: Try to update an image's property using incorrect HTTP
        method.

        1. Create an image
        2. Update image's status using PUT '/images/{image_id}'
        3. Verify the response code is 415
        """
        self.assertTrue(False, msg="Not Yet Implemented")

    @tags(type='negative', regression='true')
    def test_update_image_size(self):
        """
        @summary: Try to update an image's size property.

        1. Create an image
        2. Verify that image size is None
        2. Update image's size to a given number (e.g. 1024)
        3. Verify response code is 403
        """

        response = self.images_client.update_image(image_id=self.image.id_,
                                                   replace={"size": 1024})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_using_blank_image_id(self):
        """
        @summary: Try to update an image using blank image id.

        1. Create an image
        2. Update image wit a blank image id
        3. Verify response code is 404
        """

        response = self.images_client.update_image(
            image_id="", replace={"name": (rand_name("updated_name_"))})
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_update_image_using_invalid_image_id(self):
        """
        @summary: Try to update an image using invalid image id.

        1. Create an image
        2. Update image with invalid image id
        3. Verify response code is 404
        """

        response = self.images_client.update_image(
            image_id="invalid_image_id",
            replace={"name": (rand_name("updated_name_"))})
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_update_image_using_incorrect_request_body(self):
        """
        @summary: Try to update an image using incorrect request body.

        1. Create an image
        2. Update image with incorrect request body.
        3. Verify response code is 415
        """

        self.assertTrue(False, msg="Not Yet Implemented")

    @tags(type='negative', regression='true')
    def test_update_image_with_new_owner(self):
        """
        @summary: Try to update owner of an image.

        1. Create an image
        2. Update image with new owner.
        3. Verify response code is 403
        """

        response = self.images_client.update_image(
            image_id=self.image.id_, replace={"owner": rand_name("new_owner")})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_with_new_location(self):
        """
        @summary: Try to update location of an image.

        1. Create an image
        2. Update active image with new location.
        3. Verify response code is 403
        """

        response = self.images_client.update_image(
            image_id=self.image.id_,
            replace={"location": self.image.self_})
        self.assertEqual(response.status_code, 403)
