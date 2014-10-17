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
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudroast.compute.fixtures import ServerFromImageFixture


class CreateImageTest(object):

    @tags(type='smoke', net='no')
    def test_create_image_response_code(self):
        """Verify the response code for a create image request is correct."""
        self.assertEqual(self.image_response.status_code, 202)

    @tags(type='smoke', net='no')
    def test_new_image_in_image_list(self):
        """Verify the new image appears in the list of images."""
        images = self.images_client.list_images_with_detail().entity
        image_ids = [image.id for image in images]
        self.assertIn(self.image.id, image_ids)

    @tags(type='smoke', net='no')
    def test_get_image(self):
        """The expected image should be returned."""
        resp = self.images_client.get_image(self.image_id)
        self.assertEqual(resp.status_code, 200)

        image = resp.entity
        self.assertEqual(self.image_id, image.id)
        self.assertEqual(self.image.name, self.image_name)
        self.assertTrue(self.image.created is not None)
        self.assertTrue(self.image.updated is not None)
        self.assertGreaterEqual(self.image.updated, self.image.created)

    def test_created_image_type(self):
        """Verify the image type field was set correctly"""
        self.assertEqual(self.image.metadata.get('image_type'), 'snapshot')

    def test_image_provided_metadata(self):
        """Verify the provided metadata was set for the image"""
        for key, value in self.metadata.iteritems():
            self.assertIn(key, self.image.metadata)
            self.assertEqual(self.image.metadata.get(key), value)

    def test_image_inherited_metadata(self):
        """
        Verify the metadata of the parent image was transferred
        to the new image
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
        Verify that non-inherited metadata of the parent image was not
        transferred to the new image
        """
        for meta_elem in self.image_behaviors.read_non_inherited_metadata():
            self.assertNotIn(meta_elem, self.image.metadata)

    @tags(type='positive', net='no')
    def test_can_create_server_from_image(self):
        """Verify that a new server can be created from the image."""
        server = self.server_behaviors.create_active_server(
            image_ref=self.image_id).entity
        self.resources.add(
            server.id, self.servers_client.delete_server)
        self.assertEqual(server.image.id, self.image_id)


class ServerFromImageCreateImageTests(ServerFromImageFixture,
                                      CreateImageTest):

    @classmethod
    def setUpClass(cls):
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
