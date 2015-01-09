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
    suite.addTest(GlanceScrubberTest(
        "test_chunks_present_after_image_create"))
    suite.addTest(GlanceScrubberTest(
        "test_chunks_deleted_after_image_delete"))
    return suite


class GlanceScrubberTest(ObjectstorageIntegrationFixture):
    """
    @summary: Glance Scrubber tests module mainly tests glance scrubber
    functionality and making sure file chunks are generated in swift
    after image creation after that makes sure all those files are deleted
    after image deletion
    """

    @classmethod
    def setUpClass(cls):
        super(GlanceScrubberTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.image = cls.image_behaviors.create_active_image(
            cls.server.id).entity
        cls.prefix = {'prefix': cls.image.id}
        cls.message = "Expected {input} to be {comparison} {expectation}, was {reality}"

    @tags(type='smoke', net='no')
    def test_chunks_present_after_image_create(self):
        """The chunks are created in Cloud Files"""

        chunks = self._get_image_chunks(self.prefix)

        self.assertGreaterEqual(chunks, 1, msg=self.message.format(
            input="Image Chunks", comparison=">=", expectation=1, reality=chunks))

    @tags(type='smoke', net='no')
    def test_chunks_deleted_after_image_delete(self):
        """
        Images are stored in CF as 'chunks', just files that belong together
        in a specific order. After deletion we expect 0 chunk size
        """

        # Delete Image
        self.images_client.delete_image(self.image.id)
        self.image_behaviors.wait_for_image_to_be_deleted(self.image.id)

        chunks = self._get_image_chunks(self.prefix)

        self.assertLessEqual(chunks, 0, msg=self.message.format(input='Image Chunks',
                             comparison="<=",
                             expectation=0,
                             reality=chunks))

    def _get_image_chunks(self, prefix):
        chunks = []
        # List all containers
        containers_response = self.object_storage_client.list_containers()

        # Checking all containers for the image chunks
        for container in containers_response.entity:
            chunks_response = self.object_storage_client.list_objects(
                container.name, params=prefix)
            if chunks_response.entity is not None:
                for storage_chunk in chunks_response.entity:
                    chunks.append(storage_chunk.name)
        return chunks
