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
        "test_custom_container_present_after_image_create"))
    suite.addTest(GlanceScrubberTest(
        "test_custom_container_present_after_image_delete"))
    return suite


@unittest.skipUnless(images_config.swift_store,
                     'Functionality disabled if swift is not enabled')
class GlanceScrubberTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(GlanceScrubberTest, cls).setUpClass()
        cls.chunks = []
        cls.message = "Expected to be {0}, was {1}."
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.image = cls.image_behaviors.create_active_image(
            cls.server.id).entity
        cls.server_behaviors.wait_for_server_task_state(
            cls.server.id, 'none', cls.servers_config.server_build_timeout)
        object_storage_api = ObjectStorageComposite()
        cls.object_storage_client = object_storage_api.client
        cls.object_storage_behaviors = object_storage_api.behaviors
        cls.prefix = {'prefix': cls.image.id}
        cls.multiple_container = "{0}{1}".format(
            images_config.image_base_container,
            cls.image.id[:images_config.image_factor])

    @tags(type='smoke', net='no')
    def test_custom_container_present_after_image_create(self):
        """The container is present in Cloud Files"""

        found_container = self._get_container_from_container_list(
            self.multiple_container)

        self.assertTrue(found_container, msg=self.message.format('Container'
                        ' expected to be created with following name',
                        self.multiple_container))

    @tags(type='smoke', net='no')
    def test_custom_container_present_after_image_delete(self):
        """The container is present in Cloud Files after image delete"""
        # Delete Image
        self.images_client.delete_image(self.image.id)
        self.image_behaviors.wait_for_image_to_be_deleted(self.image.id)

        found_container = self._get_container_from_container_list(
            self.multiple_container)

        self.assertTrue(found_container, msg=self.message.format('Container'
                        ' expected to be created with following name',
                        self.multiple_container))

    def _get_container_from_container_list(self, desired_container):
        found_container = False
        # List all containers
        containers_response = self.object_storage_client.list_containers()
        # Checking all containers for the image chunks
        for container in containers_response.entity:
            if container.name == desired_container:
                found_container = True
        return found_container
