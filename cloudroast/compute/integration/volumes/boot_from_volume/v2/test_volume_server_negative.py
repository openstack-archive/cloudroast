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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import BadRequest

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class CreateVolumeServerNegativeTest(ServerFromVolumeV2Fixture):

    @unittest.skip('Bug, Redmine #8734')
    @tags(type='smoke', net='no')
    def test_delete_on_terminate_invalid(self):
        """Verify delete on termination set to invalid throws bad request"""
        # Creating block device with snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v2(
            boot_index=0, uuid=self.image_ref,
            volume_size=self.volume_size,
            source_type='image', destination_type='volume',
            delete_on_termination='invalid')
        # Try Creating Instance from Volume V2
        with self.assertRaises(BadRequest):
            self.boot_from_volume_client.create_server(
                block_device_mapping_v2=self.block_data,
                flavor_ref=self.flavors_config.primary_flavor,
                name=rand_name("server"))

    @tags(type='smoke', net='no')
    def test_source_type_invalid(self):
        """Verify source type set to invalid throws bad request"""
        # Creating block device with snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v2(
            boot_index=0, uuid=self.image_ref,
            volume_size=self.volume_size,
            source_type='invalid', destination_type='volume',
            delete_on_termination=True)
        # Try Creating Instance from Volume V2
        with self.assertRaises(BadRequest):
            self.boot_from_volume_client.create_server(
                block_device_mapping_v2=self.block_data,
                flavor_ref=self.flavors_config.primary_flavor,
                name=rand_name("server"))

    @unittest.skip('Bug, Redmine #8734')
    @tags(type='smoke', net='no')
    def test_boot_from_concurent_sources_with_image_ref_invalid(self):
        """Verify default behaviour is booting from image when image_ref is
        also provided on the create server call"""
        # Creating block device with snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v2(
            boot_index=0, uuid=self.image_ref,
            volume_size=self.volume_size,
            source_type='image', destination_type='volume',
            delete_on_termination=True)
        # Creating Instance from Volume V2
        with self.assertRaises(BadRequest):
            self.boot_from_volume_client.create_server(
                block_device_mapping_v2=self.block_data,
                flavor_ref=self.flavors_config.primary_flavor,
                name=rand_name("server"),
                image_ref=self.image_ref)

    @tags(type='smoke', net='no')
    def test_flavor_invalid(self):
        """Verify flavor set to invalid throws bad request"""
        # Creating block device with snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v2(
            boot_index=0, uuid=self.image_ref,
            volume_size=self.volume_size,
            source_type='image', destination_type='volume',
            delete_on_termination=True)
        # Try Creating Instance from Volume V2
        with self.assertRaises(BadRequest):
            self.boot_from_volume_client.create_server(
                block_device_mapping_v2=self.block_data,
                flavor_ref='invalid',
                name=rand_name("server"))
