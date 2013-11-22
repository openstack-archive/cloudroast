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
from cloudcafe.images.common.types import \
    ImageContainerFormat, ImageDiskFormat, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestUpdateImage(ImagesFixture):

    @tags(type='smoke')
    def test_update_image_replace_core_properties(self):
        """
        @summary: Replace values of core properties

        1) Create image
        2) Update image replacing all allowed core properties
        3) Verify that the response code is 200
        4) Verify that the updated properties are correct
        5) Revert protected property
        6) Verify that the response code is 200
        """

        updated_container_format = ImageContainerFormat.AKI
        updated_disk_format = ImageDiskFormat.ISO
        updated_name = rand_name('updated_image')
        updated_protected = True
        revert_protected = False
        updated_tags = rand_name('updated_tag')
        updated_visibility = ImageVisibility.PRIVATE
        image = self.images_behavior.create_new_image()
        response = self.images_client.update_image(
            image.id_, replace={'container_format': updated_container_format,
                                'disk_format': updated_disk_format,
                                'name': updated_name,
                                'protected': updated_protected,
                                'tags': [updated_tags],
                                'visibility': updated_visibility})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.checksum, image.checksum)
        self.assertEqual(updated_image.created_at, image.created_at)
        self.assertEqual(updated_image.file_, image.file_)
        self.assertEqual(updated_image.container_format,
                         updated_container_format)
        self.assertEqual(updated_image.disk_format, updated_disk_format)
        self.assertEqual(updated_image.name, updated_name)
        self.assertEqual(updated_image.id_, image.id_)
        self.assertEqual(updated_image.min_disk, image.min_disk)
        self.assertEqual(updated_image.min_ram, image.min_ram)
        self.assertEqual(updated_image.protected, updated_protected)
        self.assertEqual(updated_image.schema, image.schema)
        self.assertEqual(updated_image.self_, image.self_)
        self.assertEqual(updated_image.size, image.size)
        self.assertEqual(updated_image.status, image.status)
        self.assertEqual(updated_image.tags, [updated_tags])
        self.assertGreaterEqual(updated_image.updated_at, image.updated_at)
        self.assertEqual(updated_image.visibility, updated_visibility)
        # Need to revert protected property so that the image can be torn down
        response = self.images_client.update_image(
            image.id_, replace={'protected': revert_protected})
        self.assertEqual(response.status_code, 200)

    @tags(type='positive', regression='true')
    def test_update_image_add_additional_property(self):
        """
        @summary: Update image add additional property

        1) Create image
        2) Update image adding a new property
        3) Verify that the response code is 200
        4) Verify that the new property is in the response
        5) Verify that the new property's value is correct
        """

        new_prop = 'new_prop'
        new_prop_value = rand_name('new_prop_value')
        image = self.images_behavior.create_new_image()
        response = self.images_client.update_image(
            image.id_, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertIn(new_prop, updated_image.additional_properties)
        for prop, prop_val in updated_image.additional_properties.iteritems():
            if prop == new_prop:
                self.assertEqual(prop_val, new_prop_value)

    @tags(type='positive', regression='true')
    def test_update_image_remove_additional_property(self):
        """
        @summary: Update image remove additional property

        1) Create image
        2) Update image adding a new property
        3) Verify that the response code is 200
        4) Update image again removing the new property
        5) Verify that the response code is 200
        6) Verify that the removed property is not in the response
        """

        new_prop = 'new_prop'
        new_prop_value = rand_name('new_prop_value')
        image = self.images_behavior.create_new_image()
        response = self.images_client.update_image(
            image.id_, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        response = self.images_client.update_image(
            image.id_, remove={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertNotIn(new_prop, updated_image.additional_properties)

    @tags(type='positive', regression='true')
    def test_update_image_replace_additional_property(self):
        """
        @summary: Update image replace additional property

        1) Create image
        2) Update image adding a new property
        3) Verify that the response code is 200
        4) Update image again replacing the value of the new property
        5) Verify that the response code is 200
        6) Verify that the new property is in the response
        7) Verify that the new property's value is correct
        """

        new_prop = 'new_prop'
        new_prop_value = rand_name('new_prop_value')
        updated_new_prop_value = rand_name('updated_new_prop_value')
        image = self.images_behavior.create_new_image()
        response = self.images_client.update_image(
            image.id_, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        response = self.images_client.update_image(
            image.id_, replace={new_prop: updated_new_prop_value})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertIn(new_prop, updated_image.additional_properties)
        for prop, prop_val in updated_image.additional_properties.iteritems():
            if prop == new_prop:
                self.assertEqual(prop_val, updated_new_prop_value)
