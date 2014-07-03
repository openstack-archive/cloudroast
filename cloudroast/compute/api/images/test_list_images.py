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
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudroast.compute.fixtures import ComputeFixture


class ImageListTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageListTest, cls).setUpClass()

        networks = None
        if cls.servers_config.default_network:
            networks = [{'uuid': cls.servers_config.default_network}]

        cls.name = rand_name("server")
        first_response = cls.servers_client.create_server(
            name=cls.name, image_ref=cls.image_ref,
            flavor_ref=cls.flavor_ref, networks=networks).entity
        cls.resources.add(first_response.id,
                          cls.servers_client.delete_server)

        cls.name = rand_name("server")
        second_response = cls.servers_client.create_server(
            name=cls.name, image_ref=cls.image_ref,
            flavor_ref=cls.flavor_ref, networks=networks).entity
        cls.resources.add(second_response.id,
                          cls.servers_client.delete_server)

        cls.server1 = cls.server_behaviors.wait_for_server_status(
            first_response.id, NovaServerStatusTypes.ACTIVE).entity
        cls.server2 = cls.server_behaviors.wait_for_server_status(
            second_response.id, NovaServerStatusTypes.ACTIVE).entity

        cls.server1_id = cls.server1.id
        cls.server2_id = cls.server2.id

        image1_name = rand_name('testimage')
        image1_resp = cls.servers_client.create_image(cls.server1_id,
                                                      image1_name)
        assert image1_resp.status_code == 202
        cls.image1_id = cls.parse_image_id(image1_resp)
        cls.resources.add(cls.image1_id, cls.images_client.delete_image)

        image2_name = rand_name('testimage')
        image2_resp = cls.servers_client.create_image(cls.server2_id,
                                                      image2_name)
        assert image2_resp.status_code == 202
        cls.image2_id = cls.parse_image_id(image2_resp)
        cls.resources.add(cls.image2_id, cls.images_client.delete_image)

        cls.image_behaviors.wait_for_image_status(
            cls.image1_id, NovaImageStatusTypes.ACTIVE)
        cls.image_behaviors.wait_for_image_status(
            cls.image2_id, NovaImageStatusTypes.ACTIVE)
        cls.image_1 = cls.images_client.get_image(cls.image1_id).entity
        cls.image_2 = cls.images_client.get_image(cls.image2_id).entity

    @tags(type='smoke', net='no')
    def test_list_images_with_detail(self):
        """Detailed list of all images should contain the expected images"""
        images = self.images_client.list_images_with_detail()
        images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, images)
        self.assertIn(self.image_2.id, images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_status(self):
        """Detailed list of all images should contain the expected
        images filtered by status"""
        image_status = 'ACTIVE'
        images = self.images_client.list_images_with_detail(
            status=image_status)
        filtered_images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_name(self):
        """Detailed list of all images should contain the expected images
        filtered by name"""
        image_name = self.image_1.name
        images = self.images_client.list_images_with_detail(
            image_name=image_name)
        filtered_images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, filtered_images)
        self.assertNotIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_server_ref(self):
        """Detailed list of servers should be filtered by the
        server id of the image"""
        server_ref = self.image_2.server.links.self
        images = self.images_client.list_images_with_detail(
            server_ref=server_ref)
        filtered_images = [image.id for image in images.entity]

        self.assertNotIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_server_id(self):
        """Detailed list of servers should be filtered by server id
        from which the image was created"""
        server_id = self.server2_id
        images = self.images_client.list_images_with_detail(
            server_ref=server_id)
        filtered_images = [image.id for image in images.entity]

        self.assertNotIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_type(self):
        """The detailed list of servers should be filtered by image type"""
        type = self.image_2.metadata.get('image_type')
        images = self.images_client.list_images_with_detail(image_type=type)
        image_3 = self.images_client.get_image(self.image_ref).entity
        filtered_images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)
        self.assertNotIn(image_3.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_limit_results(self):
        """Verify only the expected number of results
        (with full details) are returned"""
        limit = 1
        images = self.images_client.list_images_with_detail(limit=1)
        self.assertEquals(
            len(images.entity), limit,
            msg="The image list length does not match the expected limit.")

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_changes_since(self):
        """Verify an update image is returned"""

        # Becoming ACTIVE will modify the updated time
        # Filter by the image's created time
        changes_since = self.image_1.created
        images = self.images_client.list_images_with_detail(
            changes_since=changes_since)
        found = any([i for i in images.entity if i.id == self.image1_id])
        self.assertTrue(
            found,
            msg="The list of images includes ones that should be excluded")

    @tags(type='positive', net='no')
    def test_list_images_with_detail_using_marker(self):
        """
        The detailed list of images should start from the provided marker
        """
        # Verify that the original image is not in the new list
        marker = self.image1_id
        images = self.images_client.list_images_with_detail(marker=marker)
        filtered_images = [image.id for image in images.entity]
        self.assertNotIn(self.image_1.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images(self):
        """The list of all images should contain the expected images"""
        images = self.images_client.list_images()
        images = [image.id for image in images.entity]
        self.assertIn(self.image_1.id, images)
        self.assertIn(self.image_2.id, images)

    @tags(type='positive', net='no')
    def test_list_images_limit_results(self):
        """Verify only the expected number of results are returned"""
        limit = 1
        images = self.images_client.list_images(limit=1)
        self.assertEquals(
            len(images.entity), limit,
            msg="The image list length does not match the expected limit.")

    @tags(type='positive', net='no')
    def test_list_images_filter_by_changes_since(self):
        """Verify only updated images are returned in the detailed list"""

        # Becoming ACTIVE will modify the updated time
        # Filter by the image's created time
        changes_since = self.image_2.created
        images = self.images_client.list_images(changes_since=changes_since)
        filtered_images = [image.id for image in images.entity]
        found = any([i for i in filtered_images if i == self.image2_id])
        self.assertTrue(
            found,
            msg="The images are not listed according to the changes since.")

    @tags(type='positive', net='no')
    def test_list_images_using_marker(self):
        """The list of images should start from the provided marker"""
        marker = self.image2_id
        images = self.images_client.list_images(marker=marker)
        filtered_images = [image.id for image in images.entity]

        # Verify the image does not exist in the filtered list
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_status(self):
        """
        The list of images should contain images with the specified status
        """
        imageStatus = NovaImageStatusTypes.ACTIVE
        images = self.images_client.list_images(status=imageStatus)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_name(self):
        """The list of images should contain images filtered by name"""
        imageName = self.image_1.name
        images = self.images_client.list_images(image_name=imageName)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_server_ref(self):
        """List of all images should contain the expected images
        filtered by server_id of the image"""
        server_ref = self.image_1.server.links.self
        images = self.images_client.list_images(server_ref=server_ref)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_server_id(self):
        """List of all images should contain the expected images filtered
        by server id from which the image was created"""
        server_id = self.server1_id
        images = self.images_client.list_images(server_ref=server_id)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_type(self):
        """The list of images should be filtered by image type"""
        type = 'snapshot'
        images = self.images_client.list_images(image_type=type)
        image3_id = self.image_ref
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertIn(self.image2_id, filtered_images)
        self.assertNotIn(image3_id, filtered_images)
