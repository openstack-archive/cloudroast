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

import sys

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.config import ComputeEndpointConfig, \
    MarshallingConfig, ComputeFuzzingConfig
from cloudcafe.compute.composites import ComputeComposite, \
    ComputeAdminComposite, ComputeIntegrationComposite
from cloudcafe.compute.common.exception_handler import ExceptionHandler


class ComputeFixture(BaseTestFixture):
    """
    @summary: Base fixture for compute tests
    """

    @classmethod
    def setUpClass(cls):
        super(ComputeFixture, cls).setUpClass()
        cls.compute = ComputeComposite()

        # Configs
        cls.flavors_config = cls.compute.flavors.config
        cls.images_config = cls.compute.images.config
        cls.servers_config = cls.compute.servers.config
        cls.compute_endpoint = ComputeEndpointConfig()
        cls.marshalling = MarshallingConfig()
        cls.config_drive_config = cls.compute.config_drive.config
        cls.cloud_init_config = cls.compute.config_drive.cloud_init_config

        # Common config values
        cls.flavor_ref = cls.flavors_config.primary_flavor
        cls.flavor_ref_alt = cls.flavors_config.secondary_flavor
        cls.image_ref = cls.images_config.primary_image
        cls.image_ref_alt = cls.images_config.secondary_image
        cls.disk_path = cls.servers_config.instance_disk_path
        cls.split_ephemeral_disk_enabled = \
            cls.servers_config.split_ephemeral_disk_enabled
        cls.ephemeral_disk_max_size = \
            cls.servers_config.ephemeral_disk_max_size
        cls.disk_format_type = cls.servers_config.disk_format_type
        cls.expected_networks = cls.servers_config.expected_networks
        cls.file_injection_enabled = \
            cls.servers_config.personality_file_injection_enabled

        # Clients
        cls.flavors_client = cls.compute.flavors.client
        cls.servers_client = cls.compute.servers.client
        cls.boot_from_volume_client = cls.compute.boot_from_volume.client
        cls.images_client = cls.compute.images.client
        cls.keypairs_client = cls.compute.keypairs.client
        cls.security_groups_client = cls.compute.security_groups.client
        cls.security_group_rule_client = \
            cls.compute.security_groups.rules_client
        cls.volume_attachments_client = cls.compute.volume_attachments.client
        cls.rescue_client = cls.compute.rescue.client
        cls.vnc_client = cls.compute.vnc_console.client
        cls.console_output_client = cls.compute.console_output.client
        cls.limits_client = cls.compute.limits.client
        cls.server_behaviors = cls.compute.servers.behaviors
        cls.volume_server_behaviors = cls.compute.boot_from_volume.behaviors
        cls.image_behaviors = cls.compute.images.behaviors
        cls.config_drive_behaviors = cls.compute.config_drive.behaviors
        cls.flavors_client.add_exception_handler(ExceptionHandler())
        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release)

    @classmethod
    def tearDownClass(cls):
        super(ComputeFixture, cls).tearDownClass()
        cls.flavors_client.delete_exception_handler(ExceptionHandler())

    @classmethod
    def parse_image_id(cls, image_response):
        """
        @summary: Extract Image Id from Image response
        @param image_response: Image response
        @type image_response: string
        @return: Image id
        @rtype: string
        """
        image_ref = image_response.headers['location']
        return image_ref.rsplit('/')[-1]

    def validate_instance_action(self, action, server_id,
                                 user_id, project_id, request_id):
        message = "Expected {0} to be {1}, was {2}."

        self.assertEqual(action.instance_uuid, server_id,
                         msg=message.format('instance id',
                                            action.instance_uuid,
                                            server_id))
        self.assertEqual(action.user_id, user_id,
                         msg=message.format('user id',
                                            action.user_id,
                                            user_id))
        self.assertEqual(action.project_id, project_id,
                         msg=message.format('project id',
                                            action.project_id,
                                            project_id))
        self.assertIsNotNone(action.start_time)
        self.assertEquals(action.request_id, request_id,
                          msg=message.format('request id',
                                             action.request_id,
                                             request_id))
        self.assertIsNone(action.message)

    def _verify_ephemeral_disk_size(self, disks, flavor,
                                    split_ephemeral_disk_enabled=False,
                                    ephemeral_disk_max_size=sys.maxint):

        ephemeral_disk_size = flavor.ephemeral_disk

        # If ephemeral disk splitting is enabled, determine the number of
        # ephemeral disks that should be present
        if split_ephemeral_disk_enabled:
            instance_ephemeral_disks = len(disks.keys())
            self.assertEqual(
                instance_ephemeral_disks,
                int(flavor.extra_specs.get('number_of_data_disks')))

            # If the ephemeral disk size exceeds the max size,
            # set the ephemeral_disk_size to the maximum ephemeral disk size
            ephemeral_disk_size = min(ephemeral_disk_max_size,
                                      ephemeral_disk_size)

        # Validate the size of each disk
        for disk, size in disks.iteritems():
            self.assertEqual(size, ephemeral_disk_size)

    @classmethod
    def _format_disk(cls, remote_client, disk, disk_format):
        remote_client.format_disk(filesystem_type=disk_format, disk=disk)

    @classmethod
    def _mount_disk(cls, remote_client, disk, mount_point):
        remote_client.create_directory(mount_point)
        remote_client.mount_disk(disk, mount_point)


class ComputeAdminFixture(ComputeFixture):
    """
    @summary: Base fixture for compute tests
    """

    @classmethod
    def setUpClass(cls):
        super(ComputeAdminFixture, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()

        cls.admin_flavors_client = cls.compute_admin.flavors.client
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_images_client = cls.compute_admin.images.client
        cls.admin_hosts_client = cls.compute_admin.hosts.client
        cls.admin_quotas_client = cls.compute_admin.quotas.client
        cls.admin_hypervisors_client = cls.compute_admin.hypervisors.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.admin_images_behaviors = cls.compute_admin.images.behaviors
        cls.admin_servers_client.add_exception_handler(ExceptionHandler())

    @classmethod
    def tearDownClass(cls):
        super(ComputeAdminFixture, cls).tearDownClass()
        cls.flavors_client.delete_exception_handler(ExceptionHandler())
        cls.resources.release()


class BlockstorageIntegrationFixture(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(BlockstorageIntegrationFixture, cls).setUpClass()
        cls.compute_integration = ComputeIntegrationComposite()
        volumes = cls.compute_integration.volumes

        cls.poll_frequency = volumes.config.volume_status_poll_frequency
        cls.volume_size = int(volumes.config.min_volume_size)
        cls.volume_type = volumes.config.default_volume_type
        cls.volume_delete_timeout = volumes.config.volume_delete_max_timeout
        cls.volume_create_timeout = volumes.config.volume_create_max_timeout
        cls.blockstorage_client = volumes.client
        cls.blockstorage_behavior = volumes.behaviors


class ServerFromImageFixture(ComputeFixture):

    @classmethod
    def create_server(cls, flavor_ref=None, key_name=None):
        """
        @summary:Creates a server from image and waits for active status
        @param flavor_ref: The flavor used to build the server.
        @type key_name: String
        @param key_name: Generated key for the instance
        @type flavor_ref: String
        @return: Response Object containing response code and
            the server domain object
        @rtype: Request Response Object
        """
        cls.server_response = cls.server_behaviors.create_active_server(
            flavor_ref=flavor_ref, key_name=key_name)
        cls.server = cls.server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        return cls.server


class ServerFromVolumeV1Fixture(BlockstorageIntegrationFixture):

    @classmethod
    def create_server(cls, flavor_ref=None, key_name=None):
        """
        @summary:Creates a server from volume V1 and waits for active status
        @param flavor_ref: The flavor used to build the server.
        @type key_name: String
        @param key_name: Generated key for the instance
        @type flavor_ref: String
        @return: Response Object containing response code and
            the server domain object
        @rtype: Request Response Object
        """
        # Creating a volume for the block device mapping
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size,
            volume_type=cls.volume_type,
            image_ref=cls.image_ref)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        # Creating block device mapping used for server creation
        cls.block_device_mapping_matrix = [{
            "volume_id": cls.volume.id_,
            "delete_on_termination": True,
            "device_name": cls.images_config.primary_image_default_device,
            "size": cls.volume_size,
            "type": ''}]
        # Creating the Boot from Volume Version 1 Instance
        cls.server_response = cls.server_behaviors.create_active_server(
            block_device_mapping=cls.block_device_mapping_matrix,
            flavor_ref=flavor_ref, key_name=key_name)
        cls.server = cls.server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        return cls.server


class ServerFromVolumeV2Fixture(BlockstorageIntegrationFixture):

    @classmethod
    def create_server(cls, flavor_ref=None, key_name=None):
        """
        @summary: Base fixture for compute tests creating the Boot from Volume
        Version 2 Instance Changes between the two versions are block device
        mapping is deprecated in favor of block device which is now creating
        the volume behind the scenes
        @param flavor_ref: The flavor used to build the server.
        @type key_name: String
        @param key_name: Generated key for the instance
        @type flavor_ref: String
        @return: Response Object containing response code and
            the server domain object
        @rtype: Request Response Object
        """
        #Creating block device used for server creation
        cls.block_device_matrix = [{
            "boot_index": 0,
            "uuid": cls.image_ref,
            "volume_size": cls.volume_size,
            "source_type": 'image',
            "destination_type": 'volume',
            "delete_on_termination": True}]
        # Creating the Boot from Volume Version 2 Instance
        cls.server_response = cls.volume_server_behaviors.create_active_server(
            block_device=cls.block_device_matrix, flavor_ref=flavor_ref,
            key_name=key_name)
        cls.server = cls.server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        return cls.server


class FlavorIdNegativeDataList(DatasetList):
    def __init__(self):
        super(FlavorIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'flavor_id': line})


class ImageIdNegativeDataList(DatasetList):
    def __init__(self):
        super(ImageIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'image_id': line})


class ServerIdNegativeDataList(DatasetList):
    def __init__(self):
        super(ServerIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'server_id': line})
