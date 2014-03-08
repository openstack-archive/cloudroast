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
from cloudcafe.common.tools.datagen import random_string
from cloudcafe.compute.composites import ComputeIntegrationComposite
from cloudroast.blockstorage.volumes_api.fixtures import VolumesTestFixture


class ComputeIntegrationTestFixture(VolumesTestFixture):

    @classmethod
    def setUpClass(cls):
        super(ComputeIntegrationTestFixture, cls).setUpClass()
        cls._compute = ComputeIntegrationComposite()
        cls.servers = cls._compute.servers
        cls.flavors = cls._compute.flavors
        cls.images = cls._compute.images
        cls.volume_attachments = cls._compute.volume_attachments

    @staticmethod
    def random_server_name():
        return random_string(prefix="Server_", size=10)

    @classmethod
    def new_server(
            cls, name=None, image=None, flavor=None, add_cleanup=True):

        name = name or cls.random_server_name()
        image = image or cls.images.config.primary_image
        flavor = flavor or cls.flavors.config.primary_flavor
        resp = cls.servers.behaviors.create_active_server(name, image, flavor)

        if add_cleanup:
            cls.addClassCleanup(
                cls.servers.client.delete_server, resp.entity.id)

        return resp.entity


class VolumesImagesIntegrationFixture(ComputeIntegrationTestFixture):

    def calculate_volume_size_for_image(self, image):
        """Get size from image object if possible, or use configured value
        TODO: Move this into a behavior
        """

        size = getattr(image, 'min_disk', None)

        # Log missing sizes
        if not size:
            msg = (
                "Image {image_id} did not report a meaningful disks size. "
                "Falling back to configured min_volume_size_from_image".format(
                    image_id=image.id))
            self.fixture_log.warning(msg)

        # If size is 0 or not reported (None), fall back to configured
        # value for min_volume_size_from_image
        return max(size, self.volumes.config.min_volume_from_image_size)

    def create_volume_from_image_test(self, volume_type, image):
        size = self.calculate_volume_size_for_image(image)
        volume = self.volumes.behaviors.create_available_volume(
            size, volume_type.id_, image_ref=image.id,
            timeout=self.volumes.config.volume_create_max_timeout)

        try:
            self.addCleanup(
                self.volumes.behaviors.delete_volume_confirmed, volume.id_)
        except:
            raise Exception(
                "Could not create a volume in setup for "
                "create_volume_from_image test")

        self.assertEquals(
            str(size), str(volume.size),
            "Expected volume size {0} did not match actual observed volume"
            " size {1}".format(size, volume.size))

        self.assertEquals(
            'true', volume.bootable, "Volume built from image was not marked "
            "as bootable")

            # TODO: Add volume metadata tests to match against image metadata
            # TODO: Add image tests to verify image was correctly built
