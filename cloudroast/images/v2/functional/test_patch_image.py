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
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class PatchImageTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_update_image_name(self):
        """Update an image's name property.

        1. Create an image
        2. Update the name of an image
        3. Verify response code is 200
        4. Verify response is an image with correct properties.
        """

        image_id = self.images_behavior.register_basic_image()
        updated_image_name = rand_name("updated_name_")
        response = self.api_client.update_image(
            image_id=image_id, replace={"name": updated_image_name})

        self.assertEqual(response.status_code, 200)

        updated_image = response.entity

        self.assertEqual(updated_image.name, updated_image_name)
        self.assertEqual(updated_image.id_, image_id)

    @tags(type='positive')
    def test_add_image_property(self):
        """
        Add an image property.

        1. Add new property to image
        2. Verify response code is 200
        3. Verify response content contains a new property and its value
        """

        image_id = self.images_behavior.register_basic_image()
        additional_property = rand_name("additional_property-")
        value_of_new_property = rand_name("value_of_new_property-")
        response = self.api_client.update_image(
            image_id=image_id,
            add={additional_property: value_of_new_property})

        self.assertEqual(response.status_code, 200)
        self.assertIn(additional_property, response.content)
        self.assertIn(value_of_new_property, response.content)

    @tags(type='positive')
    def test_update_image_new_property_value(self):
        """
        Update the value of an image new property.

        1. Add new property to image
        2. Update value of image new property
        2. Verify the response code is 200
        3. Verify the response content contains image with correct properties.
        """

        image_id = self.images_behavior.register_basic_image()
        additional_property = rand_name("additional_property-")
        value_of_new_property = rand_name("value_of_new_property-")

        response = self.api_client.update_image(
            image_id=image_id,
            add={additional_property: value_of_new_property})

        self.assertEqual(response.status_code, 200)
        self.assertIn(additional_property, response.content)
        self.assertIn(value_of_new_property, response.content)

        updated_image_new_property = rand_name("updated_new_property_value-")
        response = self.api_client.update_image(
            image_id=image_id,
            replace={additional_property: updated_image_new_property})

        self.assertEqual(response.status_code, 200)
        self.assertIn(additional_property, response.content)
        self.assertIn(updated_image_new_property, response.content)
        self.assertNotIn(value_of_new_property, response.content)

    @tags(type='positive')
    def test_remove_additional_image_property(self):
        """
        Remove an additional image property.

        1. Add new property to image
        2. Verify response code is 200
        3. Verify response content contains a new property and its value
        4. Remove added image property
        5. Verify response code is 200
        """

        image_id = self.images_behavior.register_basic_image()
        additional_property = rand_name("additional_property-")
        value_of_new_property = rand_name("value_of_new_property-")
        response = self.api_client.update_image(
            image_id=image_id,
            add={additional_property: value_of_new_property})

        self.assertEqual(response.status_code, 200)
        self.assertIn(additional_property, response.content)
        self.assertIn(value_of_new_property, response.content)

        response = self.api_client.update_image(
            image_id=image_id,
            remove={additional_property: value_of_new_property})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(additional_property, response.content)
        self.assertNotIn(value_of_new_property, response.content)

    @tags(type='positive')
    def test_update_image_with_optional_properties(self):
        """
        Update image's visibility and tags.

        1. Register an image
        2. Add a tag to the image
        3. Get the image and verify that it has correct properties
        3. Update image's visibility, tags.
        4. Verify response code is 204
        5. Verify response body contains an image with correct properties
        and optional parameters exist
        """
        image_id = self.images_behavior.register_basic_image()
        image_tag = rand_name("image_tag")

        response = self.api_client.add_tag(image_id=image_id,
                                           tag=image_tag)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity

        self.assertIn(image_tag, image.tags)
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        updated_image_tag = rand_name("updated_image_tag")
        updated_image_visibility = ImageVisibility.PUBLIC
        response = self.api_client.update_image(
            image_id=image_id,
            replace={'visibility': updated_image_visibility,
                     'tags': [updated_image_tag]})

        self.assertEqual(response.status_code, 200)
        updated_image = response.entity

        self.assertEqual(updated_image.id_, image_id)
        self.assertEqual(updated_image_visibility, updated_image.visibility)
        self.assertIn(updated_image_tag, updated_image.tags)

    @tags(type='negative')
    def test_update_image_with_invalid_visibility(self):
        """
        Try to update an image's visibility with invalid visibility.

        1. Update image's visibility with invalid visibility
        2. Verify response code is 400
        """
        image_id = self.images_behavior.register_basic_image()

        response = self.admin_api_client.get_image(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity

        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        updated_image_visibility = rand_name("invalid_visibility")
        response = self.admin_api_client.update_image(
            image_id=image_id,
            replace={"visibility": updated_image_visibility})

        self.assertEqual(response.status_code, 400)

    @tags(type='negative')
    def test_update_image_add_status(self):
        """
        Try to update an image by adding status property to it.

        1. Update image's status by adding new status property to it
        2. Verify response code is 403
        """

        image_id = self.images_behavior.register_basic_image()
        response = self.api_client.update_image(
            image_id=image_id, add={"status": rand_name("status-")})

        self.assertEqual(response.status_code, 403)

    @tags(type='negative')
    def test_update_image_remove_status(self):
        """
        Try to remove the status property from image.

        1. Update image's status, by removing it.
        2. Verify the response code is 403
        """

        image_id = self.images_behavior.register_basic_image()
        response = self.api_client.update_image(
            image_id=image_id, remove={"status": rand_name("remove")})

        self.assertEqual(response.status_code, 403)

    @tags(type='negative')
    def test_update_image_replace_status(self):
        """
        Try to replace the status property of an image.

        1. Update image's status, by replacing it.
        2. Verify the response code is 403
        """

        image_id = self.images_behavior.register_basic_image()

        response = self.api_client.update_image(
            image_id=image_id, replace={"status": rand_name("replace")})

        self.assertEqual(response.status_code, 403)

    @tags(type='negative')
    def test_update_image_using_http_method_put(self):
        """
        Try to update an image's property using incorrect HTTP method.

        1. Update image's status using PUT '/images/{image_id}'
        2. Verify the response code is 415
        """
        self.assertTrue(False, msg="Not Yet Implemented")

    @tags(type='negative')
    def test_update_image_using_larger_size(self):
        """
        Update an image's size property.

        1. Update image's size
        2. Verify response code is 204
        3. Verify response is an image with correct properties and new size
        """
        self.assertTrue(False, msg="Not Yet Implemented")

    @tags(type='negative')
    def test_update_image_using_blank_image_id(self):
        """
        Try to update an image using no image id.

        1. Update image without image id
        2. Verify response code is 404
        """
        response = self.api_client.update_image(
            image_id="", replace={"name": (rand_name("updated_name_"))})

        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_update_image_using_invalid_image_id(self):
        """
        Try to update an image using invalid image id.

        1. Update image with invalid image id
        2. Verify response code is 404
        """
        response = self.api_client.update_image(
            image_id="invalid_image_id",
            replace={"name": (rand_name("updated_name_"))})

        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_update_image_using_incorrect_request_body(self):
        """
        Try to update an image using incorrect request body.

        1. Update image with incorrect request body.
        2. Verify response code is 415
        """
        self.assertTrue(False, msg="Not Yet Implemented")

    @tags(type='negative')
    def test_update_image_with_new_owner(self):
        """
        Try to update owner of image.

        1. Update image with new owner.
        2. Verify response code is 403
        """

        image_id = self.images_behavior.register_basic_image()

        response = self.api_client.update_image(
            image_id=image_id, replace={"owner": rand_name("new_owner")})

        self.assertEqual(response.status_code, 403)

    @tags(type='negative')
    def test_update_image_with_new_location_and_active(self):
        """
        Try to update location of an active image.

        1. Update active image with new location.
        2. Verify response code is 4xx
        """
        self.assertTrue(False, msg="Not Yet Implemented")
