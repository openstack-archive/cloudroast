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

import unittest
from unittest.suite import TestSuite

from cafe.drivers.unittest.decorators import tags
from cloudcafe.objectstorage.composites import ObjectStorageComposite
from cloudcafe.compute.images_api.config import ImagesConfig

from cloudroast.compute.fixtures import ComputeFixture

images_config = ImagesConfig()


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(GlanceScrubberTest(
        "test_chunks_present_after_image_create"))
    suite.addTest(GlanceScrubberTest(
        "test_chunks_deleted_after_image_delete"))
    return suite


@unittest.skipUnless(images_config.swift_store,
                     'Functionality disabled if swift is not enabled')
class GlanceScrubberTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(GlanceScrubberTest, cls).setUpClass()
        cls.chunks = []
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.image = cls.image_behaviors.create_active_image(
            cls.server.id).entity
        cls.server_behaviors.wait_for_server_task_state(
            cls.server.id, 'none', cls.servers_config.server_build_timeout)
        object_storage_api = ObjectStorageComposite()
        cls.object_storage_client = object_storage_api.client
        cls.object_storage_behaviors = object_storage_api.behaviors
        cls.prefix = {'prefix': cls.image.id}

    @tags(type='smoke', net='no')
    def test_chunks_present_after_image_create(self):
        """The chunks are created in Cloud Files"""
        message = "Expected to be {0}, was {1}."
        # List all containers
        containers_response = self.object_storage_client.list_containers()

        # Checking all containers for the image chunks
        for container in containers_response.entity:
            chunks_response = self.object_storage_client.list_objects(
                container.name, params=self.prefix)
            if chunks_response.entity is not None:
                for storage_chunk in chunks_response.entity:
                    self.chunks.append(storage_chunk.name)
        self.assertGreaterEqual(self.chunks, 1, msg=message.format('Image'
                                'chunks expected to be greater then 0',
                                self.chunks))

    @tags(type='smoke', net='no')
    def test_chunks_deleted_after_image_delete(self):
        """The chunks are deleted in Cloud Files"""
        message = "Expected to be {0}, was {1}."
        new_chunks = []
        # Delete Image
        self.images_client.delete_image(self.image.id)
        self.image_behaviors.wait_for_image_to_be_deleted(self.image.id)

        # List all containers
        containers_response = self.object_storage_client.list_containers()

        # Checking all containers for the image chunks
        for container in containers_response.entity:
            chunks_response = self.object_storage_client.list_objects(
                container.name, params=self.prefix)
            if chunks_response.entity is not None:
                for storage_chunk in chunks_response.entity:
                    new_chunks.append(storage_chunk.name)
        self.assertLessEqual(new_chunks, 0, msg=message.format('Image'
                             'chunks expected to be 0',
                             new_chunks))
