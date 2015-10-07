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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


class CreateImageTest(object):

    @tags(type='smoke', net='no')
    def test_create_image_response_code(self):
        """
        The response to a create image request should be 202

        Validate that the response to the image request in the test set up
        has a status code of 202.

        The following assertions occur:
            - The response code is equal to 202
        """
        self.assertEqual(self.image_response.status_code, 202)

    @tags(type='smoke', net='no')
    def test_new_image_in_image_list(self):
        """
        Verify the new image appears in the list of images.

        As the test user get a detailed list of images. The image identified
        during test set up should appear in this list.

        The following assertions occur:
            - The image id identified during test set up is found in the
              detailed list of images
        """
        images = self.images_client.list_images_with_detail().entity
        image_ids = [image.id for image in images]
        self.assertIn(self.image.id, image_ids)

    @tags(type='smoke', net='no')
    def test_get_image(self):
        """
        Getting an image's details should return the expected image details

        As the test user request the image details. Confirm that the get image
        response code is 200. Validate that the image id and image name match
        the values set during test set up. Validate that there is a created and
        updated value for the image. Validate that the updated and created
        values for the image are equal.

        The following assertions occur:
            - The response code to a get image request is 200
            - The image id in the image details of an image retrieved by image
              id matches the id value identified during test set up.
            - The image name in the image details of an image retrieved by image
              id matches the name value identified during test set up.
            - The image created value is not None
            - The image updated value is not None
            - The image created and image updated values are equal
        """
        resp = self.images_client.get_image(self.image_id)
        self.assertEqual(resp.status_code, 200)

        image = resp.entity
        self.assertEqual(self.image_id, image.id)
        self.assertEqual(self.image.name, self.image_name)
        self.assertTrue(self.image.created is not None)
        self.assertTrue(self.image.updated is not None)
        self.assertGreaterEqual(self.image.updated, self.image.created)

    def test_created_image_type(self):
        """
        An image created from a server should have a type of 'snapshot'

        Validate that the metadata value for 'image type' for the image
        identified during test set up is 'snapshot'.

        The following assertions occur:
            - The value of the 'image_type' metadata for the image is equal to
              'snapshot'
        """
        self.assertEqual(self.image.metadata.get('image_type'), 'snapshot')

    def test_image_provided_metadata(self):
        """
        Verify the provided metadata was set for the image

        The keys in the metadata dictionary identified during test set up should
        be found in the metadata for the image identified during test set up.
        The value for each key should be equal to the values for the
        corresponding key in the image metadata.

        The following assertions occur:
            - Each key in the metadata dictionary from test set up should be in
              the metadata for the image
            - The value for each key in the metadata dictionary should be equal
              to the value for that key in the image metadata
        """
        for key, value in self.metadata.iteritems():
            self.assertIn(key, self.image.metadata)
            self.assertEqual(self.image.metadata.get(key), value)

    def test_image_inherited_metadata(self):
        """
        A snapshot should inherit some of the parent images's metadata

        Using the image ref from the test configuration get the image details
        and identify this image as the 'original image'. For each key, value
        pair in the original image, validate that the key is found in the
        metadata for the snapsho identified during test set up. First check to
        see if the key is found in the non_inherited_metadata values set during
        test configuration. If the key is not found check to see if the key is either
        'image_type', 'instance_uuid' or 'user_id'. If it is not confirm that
        the value for the key in the orginal image metadata is equal to the
        value of the key in the image metadata. However if the key is equal to
        'instance_uuid' confirm that the image metadata value for that key is
        equal to the instance id identified during test setup. If the key is
        equal to user_id, confirm that the image metadata for that key is equal
        to the user id value set during test configuration.

        The following assertions occur:
            - If a key in the original image metadata is not in the
              non_inherited_metadata test configuration value and is not
              'image_type', 'instance_uuid' or 'user_id' the value of the key
              in the original image metadata should be equal to the value of the
              key in the image metadata
            - If a key in the original image metadata is not in the
              non_inherited_metadata test configuration value and is not
              'image_type', 'instance_uuid' or 'user_id' and the key is equal to
              'instance_uuid' the value of the key in the image metadata should
              be equal to the instance id identified during test set up
            - If a key in the original image metadata is not in the
              non_inherited_metadata test configuration value and is not
              'image_type', 'instance_uuid' or 'user_id' and the key is equal to
              'user_id' the value of the key in the image metadata should
              be equal to the admin user value identified during test
              configuration
        """
        intended_changed_meta = ['image_type', 'instance_uuid',
                                 'user_id']
        original_image = self.images_client.get_image(self.image_ref).entity
        for key, value in original_image.metadata.iteritems():
            # The image_type field should be the only field that differs
            # from the original image
            if key not in self.image_behaviors.read_non_inherited_metadata():
                if key not in intended_changed_meta:
                    self.assertIn(key, self.image.metadata)
                    self.assertEqual(self.image.metadata.get(key), value)
                elif key == 'instance_uuid':
                    self.assertEqual(self.image.metadata.get(key),
                                     self.server.id)
                elif key == 'user_id':
                    self.assertEqual(self.image.metadata.get(key),
                                     self.user_config.user_id)

    def test_image_not_inherited_metadata(self):
        """
        A snapshot should not inherit some of the parent image's metadata

        Validate that values in the non_inherited_metadata list identified
        during test configuration are not found as keys in the metadata of the
        image identified during test set up.

        The following assertions occur:
            - None of the values identified in non_inherited_metadata during
              test configuration should be found in the keys of the snapshot's
              metadata
        """
        for meta_elem in self.image_behaviors.read_non_inherited_metadata():
            self.assertNotIn(meta_elem, self.image.metadata)

    @tags(type='positive', net='no')
    def test_can_create_server_from_image(self):
        """
        Verify that a new server can be created from a snapsho.

        Using the snapshot identified during test set up. Create and active
        server and validate that the image id shown in the server response is
        equal to the snapshot's id.

        The following assertions occur:
            - The image id of a server created using the snapshop from the test
              set up is equal to the snapshot's id
        """
        server = self.server_behaviors.create_active_server(
            image_ref=self.image_id).entity
        self.resources.add(
            server.id, self.servers_client.delete_server)
        self.assertEqual(server.image.id, self.image_id)


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.IRONIC],
    'Create image not supported in current configuration.')
class ServerFromImageCreateImageTests(ServerFromImageFixture,
                                      CreateImageTest):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this setup:
            - A dictionary of metadata with the values:
                {'user_key1': 'value1',
                 'user_key2': 'value2'}

        The following resources are created during this setup:
            - A server with values from the test configuration
            - An image from the newly created server with metadata values from
              the metadata dictionary generated during the set up class

        """
        super(ServerFromImageCreateImageTests, cls).setUpClass()
        cls.create_server()
        cls.image_name = rand_name('image')
        cls.metadata = {'user_key1': 'value1',
                        'user_key2': 'value2'}
        server_id = cls.server.id
        cls.image_response = cls.image_behaviors.create_active_image(
            server_id, cls.image_name, metadata=cls.metadata)
        cls.image_id = cls.parse_image_id(cls.image_response)
        cls.resources.add(cls.image_id, cls.images_client.delete_image)
        cls.image = cls.image_response.entity
