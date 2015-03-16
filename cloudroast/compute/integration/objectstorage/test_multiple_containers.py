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

from unittest.suite import TestSuite

from cafe.drivers.unittest.decorators import tags

from cloudroast.compute.fixtures import ObjectstorageIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(MultipleContainersTest(
        "test_custom_container_present_after_image_create"))
    suite.addTest(MultipleContainersTest(
        "test_custom_container_present_after_image_delete"))
    return suite


class MultipleContainersTest(ObjectstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(MultipleContainersTest, cls).setUpClass()
        cls.chunks = []
        cls.message = "Expected to be {0}, was {1}."
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.image = cls.image_behaviors.create_active_image(
            cls.server.id).entity
        cls.prefix = {'prefix': cls.image.id}
        cls.multiple_container = "{0}{1}".format(
            cls.images_config.image_base_container,
            cls.image.id[:cls.images_config.image_factor])
        cls.message = "Expected container with name of {0}, but it was not found"

    @tags(type='smoke', net='no')
    def test_custom_container_present_after_image_create(self):
        """The container is present in Cloud Files"""

        found_container = self._get_container_from_container_list(
            self.multiple_container)

        self.assertTrue(found_container, msg=self.message.format(self.multiple_container))

    @tags(type='smoke', net='no')
    def test_custom_container_present_after_image_delete(self):
        """The container is present in Cloud Files after image delete"""
        # Delete Image
        self.images_client.delete_image(self.image.id)
        self.image_behaviors.wait_for_image_to_be_deleted(self.image.id)

        found_container = self._get_container_from_container_list(
            self.multiple_container)

        self.assertTrue(found_container, msg=self.message.format(self.multiple_container))

    def _get_container_from_container_list(self, desired_container):
        found_container = False
        # List all containers
        containers_response = self.object_storage_client.list_containers()
        # Checking all containers for the image chunks
        for container in containers_response.entity:
            if container.name == desired_container:
                found_container = True
        return found_container
