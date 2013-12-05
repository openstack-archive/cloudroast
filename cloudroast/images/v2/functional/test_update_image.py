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
from cloudcafe.images.common.types import ImageVisibility, \
    ImageContainerFormat, ImageDiskFormat
from cloudroast.images.fixtures import ImagesFixture


class UpdateImageTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(UpdateImageTest, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image()

    @classmethod
    def tearDownClass(cls):
        super(UpdateImageTest, cls).tearDownClass()

    @tags(type='smoke', regression='true')
    def test_update_image_name(self):
        """@summary: Update the name of an image

        1. Create an image
        2. Update the name of the image
        3. Verify response code is 200
        4. Verify response is an image with correct properties.
        """

        updated_image_name = rand_name("updated_name_")

        response = self.images_client.update_image(
            image_id=self.image.id_, replace={"name": updated_image_name})

        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.name, updated_image_name)
        self.assertEqual(updated_image.id_, self.image.id_)

    @tags(type='positive', regression='true')
    def test_add_image_property(self):
        """
        @summary: Add a new property to an image.

        1. Create an image
        2. Add new property to an image
        2. Verify response code is 200
        3. Verify response content contains a new property and its value
        """

        new_property = rand_name("new_property-")
        new_property_value = rand_name("new_property_value-")

        response = self.images_client.update_image(
            image_id=self.image.id_,
            add={new_property: new_property_value})
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_property, response.content)
        self.assertIn(new_property_value, response.content)

    @tags(type='positive', regression='true')
    def test_update_image_new_property_value(self):
        """
        @summary: Update the value of an image new property.

        1. Create an image
        2. Add new property to image
        2. Update value of image new property
        2. Verify the response code is 200
        3. Verify the response content contains image with correct properties.
        """

        new_property = rand_name("new_property")
        new_property_value = rand_name("new_property_value")

        response = self.images_client.update_image(
            image_id=self.image.id_,
            add={new_property: new_property_value})
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_property, response.content)
        self.assertIn(new_property_value, response.content)

        updated_image_new_property = rand_name("updated_new_property_value-")
        response = self.images_client.update_image(
            image_id=self.image.id_,
            replace={new_property: updated_image_new_property})

        self.assertEqual(response.status_code, 200)
        self.assertIn(new_property, response.content)
        self.assertIn(updated_image_new_property, response.content)
        self.assertNotIn(new_property_value, response.content)

    @tags(type='positive', regression='true')
    def test_remove_additional_image_property(self):
        """
        @summary: Remove an additional property of an image.

        1. Create an image
        2. Add new property to the image
        3. Verify response code is 200
        4. Verify response content contains a new property and its value
        5. Remove added image property
        6. Verify response code is 200
        7. Verify that the added image property has been removed
        """

        new_property = rand_name("new_property_")
        new_property_value = rand_name("new_property_value")

        response = self.images_client.update_image(
            image_id=self.image.id_,
            add={new_property: new_property_value})
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_property, response.content)
        self.assertIn(new_property_value, response.content)

        response = self.images_client.update_image(
            image_id=self.image.id_,
            remove={new_property: new_property_value})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(new_property, response.content)
        self.assertNotIn(new_property_value, response.content)

    @tags(type='positive', regression='true')
    def test_update_image_visibility_and_tag(self):
        """
        @summary: Update image's visibility and tag.

        1. Create an image
        2. Add a tag to the image
        3. Get the image and verify that it has correct properties
        4. Update image's visibility and tag.
        5. Verify response code is 204
        6. Verify response body contains an image with correct properties
        """

        image_tag = rand_name("image_tag")
        updated_image_tag = rand_name("updated_image_tag")
        updated_image_visibility = ImageVisibility.PUBLIC

        response = self.images_client.add_tag(image_id=self.image.id_,
                                              tag=image_tag)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertIn(image_tag, image.tags)
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        response = self.images_client.update_image(
            image_id=self.image.id_,
            replace={'visibility': updated_image_visibility,
                     'tags': [updated_image_tag]})

        self.assertEqual(response.status_code, 200)
        updated_image = response.entity

        self.assertEqual(updated_image.id_, self.image.id_)
        self.assertEqual(updated_image_visibility, updated_image.visibility)
        self.assertNotIn(image_tag, updated_image.tags)
        self.assertIn(updated_image_tag, updated_image.tags)

    @tags(type='negative', regression='true')
    def test_update_image_with_data_of_existing_image(self):
        """
        @summary: Update image with data of existing image

        1. Create an image
        2. Create another image (new_image)
        3. Update image with data of new_image
        4. Verify that response code is 200
        """

        new_image = self.images_behavior.create_new_image(
            name=rand_name("new-image"),
            visibility=ImageVisibility.PUBLIC,
            container_format=ImageContainerFormat.AMI,
            disk_format=ImageDiskFormat.ISO, tags=[rand_name("tag")])

        response = self.images_client.update_image(
            image_id=self.image.id_,
            replace={"name": new_image.name,
                     "visibility": new_image.visibility,
                     "container_format": new_image.container_format,
                     "disk_format": new_image.disk_format,
                     "tags": new_image.tags})
        self.assertEqual(response.status_code, 200)

        updated_image = response.entity
        self.assertEqual(updated_image.id_, self.image.id_)
        self.assertEqual(updated_image.name, new_image.name)
        self.assertEqual(updated_image.visibility, new_image.visibility)
        self.assertEqual(updated_image.container_format,
                         new_image.container_format)
        self.assertEqual(updated_image.disk_format, new_image.disk_format)
        self.assertEqual(updated_image.tags, new_image.tags)
