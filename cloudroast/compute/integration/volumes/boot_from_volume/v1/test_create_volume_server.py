"""
Copyright 2014 Rackspace

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

import base64

from cloudcafe.common.tools.datagen import rand_name

from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture
from cloudroast.compute.instance_actions.api.test_create_server import \
    CreateServerTest
from cloudroast.compute.integration.volumes.boot_from_volume.v2.test_create_volume_server import \
    CreateVolumeServerTest


class ServerFromVolumeV1CreateServerTests(ServerFromVolumeV1Fixture,
                                          CreateServerTest,
                                          CreateVolumeServerTest):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV1CreateServerTests, cls).setUpClass()
        # Initialzing instance name, metadata, files, keys, networking
        cls.name = rand_name("server")

        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}

        networks = None
        if cls.servers_config.default_network:
            networks = [{'uuid': cls.servers_config.default_network}]

        files = []
        if cls.file_injection_enabled:
            cls.file_contents = 'This is a test file.'
            separator = cls.images_config.primary_image_path_separator
            cls.file_path = separator.join(
                [cls.servers_config.default_file_path, 'test.txt'])
            files = [{'path': cls.file_path, 'contents': base64.b64encode(
                cls.file_contents)}]

        key_response = cls.keypairs_client.create_keypair(rand_name("key"))
        if key_response.entity is None:
            raise Exception(
                "Response entity of create key was not set. "
                "Response was: {0}".format(key_response.content))
        cls.key = key_response.entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        # Creating a volume for the block device mapping
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size,
            volume_type=cls.volume_type,
            image_ref=cls.image_ref)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        # Creating block device mapping used for server creation
        cls.block_data = cls.server_behaviors.create_block_device_mapping_v1(
            device_name=cls.images_config.primary_image_default_device,
            size=cls.volume_size, volume_id=cls.volume.id_, type='',
            delete_on_termination=True)
        # Creating Instance from Volume V1
        cls.create_resp = cls.server_behaviors.create_active_server(
            name=cls.name, flavor_ref=cls.flavors_config.primary_flavor,
            metadata=cls.metadata, personality=files, key_name=cls.key.name,
            networks=networks, block_device_mapping=cls.block_data)
        cls.server = cls.create_resp.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.flavor = cls.flavors_client.get_flavor_details(
            cls.flavor_ref).entity
