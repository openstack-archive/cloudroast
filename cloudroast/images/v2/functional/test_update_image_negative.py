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
from cloudcafe.images.common.types import ImageStatus
from cloudroast.images.fixtures import ImagesFixture


class TestUpdateImageNegative(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestUpdateImageNegative, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image()

    @tags(type='negative', regression='true')
    def test_update_image_replace_core_property(self):
        """
        @summary: Update image replace core property

        1) Create image
        2) Update image replacing the status core property
        3) Verify that the response code is 403
        """

        updated_status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            self.image.id_, replace={'status': updated_status})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_add_core_property(self):
        """
        @summary: Update image add core property

        1) Create image
        2) Update image adding the status core property
        3) Verify that the response code is 403
        """

        status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            self.image.id_, add={"status": status})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_remove_core_property(self):
        """
        @summary: Update image remove core property

        1) Create image
        2) Update image removing the status core property
        3) Verify that the response code is 403
        """

        response = self.images_client.update_image(
            self.image.id_, remove={'status': ImageStatus.QUEUED})
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_update_image_using_blank_image_id(self):
        """
        @summary: Update image using blank image id

        1) Patch image using blank image id
        2) Verify that the response code is 404
        """

        image_id = ''
        new_prop = 'new_prop'
        new_prop_value = rand_name('new_prop_value')
        response = self.images_client.update_image(
            image_id, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_update_image_using_invalid_image_id(self):
        """
        @summary: Update image using invalid image id

        1) Update image using invalid image id
        2) Verify that the response code is 404
        """

        image_id = 'invalid'
        new_prop = 'new_prop'
        new_prop_value = rand_name('new_prop_value')
        response = self.images_client.update_image(
            image_id, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 404)
