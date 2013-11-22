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

        1) Given a previously created image, update image replacing the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        updated_status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            self.image.id_, replace={'status': updated_status})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(self.image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, self.image.status)
        self.images_behavior.validate_image(self.image)

    @tags(type='negative', regression='true')
    def test_update_image_add_core_property(self):
        """
        @summary: Update image add core property

        1) Given a previously created image, update image adding the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            self.image.id_, add={"status": status})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(self.image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, self.image.status)
        self.images_behavior.validate_image(self.image)

    @tags(type='negative', regression='true')
    def test_update_image_remove_core_property(self):
        """
        @summary: Update image remove core property

        1) Given a previously created image, update image removing the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        response = self.images_client.update_image(
            self.image.id_, remove={'status': ImageStatus.QUEUED})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(self.image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, self.image.status)
        self.images_behavior.validate_image(self.image)

    @tags(type='negative', regression='true')
    def test_update_image_using_blank_image_id(self):
        """
        @summary: Update image using blank image id

        1) Update image using blank image id
        2) Verify that the response code is 404
        """

        self._update_negative_image('')

    @tags(type='negative', regression='true')
    def test_update_image_using_invalid_image_id(self):
        """
        @summary: Update image using invalid image id

        1) Update image using invalid image id
        2) Verify that the response code is 404
        """

        self._update_negative_image('invalid')

    def _update_negative_image(self, image_id=None):
            """@summary: Update negative image"""

            if image_id is None:
                image_id = self.image.id_
            response = self.images_client.update_image(
                image_id, add={'new_prop': rand_name('new_prop_value')})
            self.assertEqual(response.status_code, 404)
