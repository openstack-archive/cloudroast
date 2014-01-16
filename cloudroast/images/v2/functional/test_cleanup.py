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
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestImagesCleanUp(ComputeIntegrationFixture):

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

        # delete are servers on the account
        count = 1
        response = self.servers_client.list_servers()
        servers = response.entity
        print '{0} servers'.format(len(servers))
        for server in servers:
            self.servers_client.delete_server(server_id=server.id)
            print '{0} - deleted {1}'.format(count, server.id)
            count += 1

        #first with primary user
        count = 1
        owner = self.user_config.tenant_id
        images = self.images_behavior.list_images_pagination(owner=owner)
        print '{0} images for primary user'.format(len(images))
        for image in images:
            response = self.images_client.update_image(
                image.id_, replace={'protected': False})
            self.assertEqual(response.status_code, 200)
            response = self.images_client.delete_image(image.id_)
            self.assertEqual(response.status_code, 204)
            print '{0} - deleted {1}'.format(count, image.id_)
            count += 1
        images = self.images_behavior.list_images_pagination(owner=owner)
        self.assertListEqual(images, [])

        #now with the alt user
        count = 1
        owner = self.alt_user_config.tenant_id
        images = self.alt_images_behavior.list_images_pagination(owner=owner)
        print '{0} images for alternate user'.format(len(images))
        for image in images:
            response = self.alt_images_client.update_image(
                image.id_, replace={'protected': False})
            self.assertEqual(response.status_code, 200)
            response = self.alt_images_client.delete_image(image.id_)
            self.assertEqual(response.status_code, 204)
            print '{0} - deleted {1}'.format(count, image.id_)
            count += 1
        images = self.alt_images_behavior.list_images_pagination(owner=owner)
        self.assertListEqual(images, [])

        #now with the third user
        count = 1
        owner = self.third_user_config.tenant_id
        images = self.third_images_behavior.list_images_pagination(owner=owner)
        print '{0} images for third user'.format(len(images))
        for image in images:
            response = self.third_images_client.update_image(
                image.id_, replace={'protected': False})
            self.assertEqual(response.status_code, 200)
            response = self.third_images_client.delete_image(image.id_)
            self.assertEqual(response.status_code, 204)
            print '{0} - deleted {1}'.format(count, image.id_)
            count += 1
        images = self.third_images_behavior.list_images_pagination(owner=owner)
        self.assertListEqual(images, [])
