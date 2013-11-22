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
from cloudroast.images.fixtures import ImagesFixture


class TestImagesCleanUp(ImagesFixture):

    @tags(type='glance-cleanup')
    def test_images_cleanup(self):
        """
        @summary: Cleanup images

        1) Get images accounting for pagination using primary user as owner
        filter
        2) Update image setting each image's protected property to false
        3) Verify that the response code is 200
        4) Delete image as each one is returned
        5) Verify that the response code is 204
        6) Get images accounting for pagination using primary user as owner
        filter again
        7) Verify that no images are returned
        """

        owner = self.user_config.tenant_id
        images = self.images_behavior.list_images_pagination(owner=owner)
        for image in images:
            response = self.images_client.update_image(
                image.id_, replace={'protected': False})
            self.assertEqual(response.status_code, 200)
            response = self.images_client.delete_image(image.id_)
            self.assertEqual(response.status_code, 204)
        images = self.images_behavior.list_images_pagination(owner=owner)
        self.assertListEqual(images, [])
