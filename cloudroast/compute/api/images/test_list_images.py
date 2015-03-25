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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudroast.compute.fixtures import ComputeFixture


class ImageListTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this setup:
            - A name value that is a random name starting with the word 'server'
            - A image1_name value that is a random name starting with the word
              'testimage'
            - A image2_name value that is a random name starting with the word
              'testimage'

        The following resources are created during this setup:
            - A server using the name value and remaining required values for
              a server create request from test configuration. This server is
              referred to as server1.
            - A server using the name value and remaining required values for
              a server create request from test configuration. This server is
              referred to as sever2.
            - An image created using the image_1 name value and the server id
              of server1
            - An image created using the image_2 name value and the server id
              of server2

        The following assertions occur:
            - The status code of the create image response for image_1 is equal
              to 202
            - The status code of the create image response for image_2 is equal
              to 202
        """
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
        """
        A detailed list of all images should contain the expected images

        Request a detailed list of images. Validate that the two images created
        during test set up are found in the detailed list.

        The following assertions occur:
            - The first image created during test configuration is found in the
              detailed list of images
            - The second image created during test configuration is found in the
              detailed list of images
        """
        images = self.images_client.list_images_with_detail()
        images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, images)
        self.assertIn(self.image_2.id, images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_status(self):
        """
        A detailed list of images should respect the status filter

        Request a list of images using the value 'ACTIVE' as the status value.
        Validate that the two images created during test set up are found in the
        detailed list.

        The following assertions occur:
            - The first image created during test configuration is found in the
              detailed list of images
            - The second image created during test configuration is found in the
              detailed list of images
        """
        image_status = 'ACTIVE'
        images = self.images_client.list_images_with_detail(
            status=image_status)
        filtered_images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_name(self):
        """
        A detailed list of images should respect the name filter

        Request a list of images using the name of the first image created
        during test set up as the name value. Validate that the first image
        created during test set up is found in the detailed list and that the
        second image created during test set up is not.

        The following assertions occur:
            - The first image created during test configuration is found in the
              detailed list of images
            - The second image created during test configuration is not found
              in the detailed list of images
        """
        image_name = self.image_1.name
        images = self.images_client.list_images_with_detail(
            image_name=image_name)
        filtered_images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, filtered_images)
        self.assertNotIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_server_ref(self):
        """
        A detailed list of images should respect the server ref filter

        Request a list of images using the server ref of the first image created
        during test set up as the server ref value. Validate that the first
        image created during test set up is found in the detailed list and that
        the second image created during test set up is not.

        The following assertions occur:
            - The first image created during test configuration is found in the
              detailed list of images
            - The second image created during test configuration is not found
              in the detailed list of images
        """
        server_ref = self.image_2.server.links.self
        images = self.images_client.list_images_with_detail(
            server_ref=server_ref)
        filtered_images = [image.id for image in images.entity]

        self.assertNotIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_server_id(self):
        """
        A detailed list of images should respect the server ref filter

        Request a list of images using the server id of the first image created
        during test set up as the server ref value. Validate that the first
        image created during test set up is found in the detailed list and that
        the second image created during test set up is not.

        The following assertions occur:
            - The first image created during test configuration is found in the
              detailed list of images
            - The second image created during test configuration is not found
              in the detailed list of images
        """
        server_id = self.server2_id
        images = self.images_client.list_images_with_detail(
            server_ref=server_id)
        filtered_images = [image.id for image in images.entity]

        self.assertNotIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_type(self):
        """
        A detailed list of images should respect the image type filter

        Request a detailed list of images using the image type of the second
        image created during test set up as the image type value. Validate that
        the first and second images created during test set up are found in the
        detailed list. Validate that the image from test configuration (of a
        different image type) is not found.

        The following assertions occur:
            - The first image created during test configuration is found in the
              detailed list of images
            - The second image created during test configuration is found in
              the detailed list of images
            - The image from test configurations is not found in the detailed
              of images
        """
        type = self.image_2.metadata.get('image_type')
        images = self.images_client.list_images_with_detail(image_type=type)
        image_3 = self.images_client.get_image(self.image_ref).entity
        filtered_images = [image.id for image in images.entity]

        self.assertIn(self.image_1.id, filtered_images)
        self.assertIn(self.image_2.id, filtered_images)
        self.assertNotIn(image_3.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_with_detail_limit_results(self):
        """
        A detailed list of images should respect the page size requested

        Get a detailed list of images with a page size of 1. Validate that
        the images list returned contains only one image.

        The following assertions occur:
            - The detailed image list requested by the test user with a page
              size value of "1" contains only one image
        """
        limit = 1
        images = self.images_client.list_images_with_detail(limit=1)
        self.assertEquals(
            len(images.entity), limit,
            msg="The image list length does not match the expected limit.")

    @tags(type='positive', net='no')
    def test_list_images_with_detail_filter_by_changes_since(self):
        """
        A detailed list of images should respect the changes since filter

        Get a detailed list of images using the 'created' value of the first
        image created during test set up as the 'changes since' filter value.
        Validate that the first image is found in the detailed list of images.

        The following assertions occur:
            - The first image created during test configuration is found in the
              detailed list of images
        """
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
        A detailed list of images should start from the provided marker

        Get a detailed list of images using the image id of the first image
        created during test set up as the 'marker' value. Validate that the
        first image created during test set up is not found in the detailed
        list.

        The following assertions occur:
            - The first image created during test configuration is not found in
              the detailed list of images
        """
        # Verify that the original image is not in the new list
        marker = self.image1_id
        images = self.images_client.list_images_with_detail(marker=marker)
        filtered_images = [image.id for image in images.entity]
        self.assertNotIn(self.image_1.id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images(self):
        """
        A list of all images should contain the expected images

        Request a list of images. Validate that the two images created during
        test set up are found in the list.

        The following assertions occur:
            - The first image created during test configuration is found in the
              list of images
            - The second image created during test configuration is found in the
              list of images
        """
        images = self.images_client.list_images()
        images = [image.id for image in images.entity]
        self.assertIn(self.image_1.id, images)
        self.assertIn(self.image_2.id, images)

    @tags(type='positive', net='no')
    def test_list_images_limit_results(self):
        """
        A list of images should respect the page size requested

        Get a list of images with a page size of 1. Validate that the images
        list returned contains only one image.

        The following assertions occur:
            - The detailed image list requested by the test user with a page
              size of 1 contains only one image
        """
        limit = 1
        images = self.images_client.list_images(limit=1)
        self.assertEquals(
            len(images.entity), limit,
            msg="The image list length does not match the expected limit.")

    @tags(type='positive', net='no')
    def test_list_images_filter_by_changes_since(self):
        """
        A list of images should respect the changes since filter

        Get a list of images using the 'created' value of the first image
        created during test set up as the 'changes since' filter value. Validate
        that the first image is found in the list of images.

        The following assertions occur:
            - The second image created during test configuration is found in
              the list of images
        """

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
        """
        A list of images should start from the provided marker

        Get a list of images using the image id of the first image created
        during test set up as the 'marker' value. Validate that the first image
        created during test set up is not found in the list.

        The following assertions occur:
            - The first image created during test configuration is not found in
              the list of images
        """
        marker = self.image2_id
        images = self.images_client.list_images(marker=marker)
        filtered_images = [image.id for image in images.entity]

        # Verify the image does not exist in the filtered list
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_status(self):
        """
        A filtered list of images should respect image status value

        Request a list of images using the 'ACTIVE' status value as the image
        status value. Validate that the image ids of image1 and image2, which
        were created during test set up, are in the list of images

        The following assertions occur:
            - The image id for image1 is found in the list of images filtered
              by image status value of 'ACTIVE'
            - The image id for image2 is found in the list of images filtered
              by image status value of 'ACTIVE'
        """
        imageStatus = NovaImageStatusTypes.ACTIVE
        images = self.images_client.list_images(status=imageStatus)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_name(self):
        """
        A filtered list of list of images should respect image name value

        Request a list of images using the name of image1 created during test
        set up as the image name value. Validate that the image id of image1
        created during test set up is in the list of images. Validate that the
        image id of image2 created during test set up is not in the list of
        images.

        The following assertions occur:
            - The image id for image1 is found in the list of images filtered
              by image name value of the name of image1
            - The image id for image2 is not found in the list of images
              filtered by image name value of the name of image1
        """
        imageName = self.image_1.name
        images = self.images_client.list_images(image_name=imageName)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_server_ref(self):
        """
        A filtered list of images should respect server ref value

        Request a list of images using the server ref of image1 created during
        test set up as the server ref filter value. Validate that the image id
        of image1 created during test set up is in the list of images. Validate
        that the image id of image2 created during set up is not in the list of
        images.

        The following assertions occur:
            - The image id for image1 is found in the list of images filtered
              by server ref value of the server value of image1
            - The image id for image2 is not found in the list of images
              filtered by server ref value of the server value of image1
        """

        server_ref = self.image_1.server.links.self
        images = self.images_client.list_images(server_ref=server_ref)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_server_id(self):
        """
        A filtered list of images should respect server ref value

        Request a list of images using the server id of server1 created during
        test set up as the server ref filter value. Validate that the image
        id of image1 created during test set up is in the list of images.
        Validate that the image id of image2 created during set up is not in
        the list of images.

        The following assertions occur:
            - The image id for image1 is found in the list of images filtered
              by server ref value of server1
            - The image id for image2 is not found in the list of images
              filtered by server ref value of server1
        """
        server_id = self.server1_id
        images = self.images_client.list_images(server_ref=server_id)
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertNotIn(self.image2_id, filtered_images)

    @tags(type='positive', net='no')
    def test_list_images_filter_by_type(self):
        """
        A filtered list of images should respect image type value

        Request a list of images using the image type value of 'snapshot'.
        Validate that the image ids of image1 and image2 created during test
        set up are in the list of images. Validate that the image ref from test
        configuration is not in the list of images.

        The following validations occur:
            - The image1 id of the image created during test set up is in the
              list of images filtered by image type 'snapshot'
            - The image1 id of the image created during test set up is in the
              list of images filtered by image type 'snapshot'
            - The image id of the image ref from test configuration is not in
              the list of images filtered by image type 'snapshot'
        """
        type = 'snapshot'
        images = self.images_client.list_images(image_type=type)
        image3_id = self.image_ref
        filtered_images = [image.id for image in images.entity]
        self.assertIn(self.image1_id, filtered_images)
        self.assertIn(self.image2_id, filtered_images)
        self.assertNotIn(image3_id, filtered_images)
