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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import BadRequest
from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture

class CreateVolumeV1ServerNegativeTest(ServerFromVolumeV1Fixture):

    @tags(type='smoke', net='no')
    def test_device_name_invalid(self):
        """Verify device type set to SSD throws bad request"""
        # Creating block device
        # Attempted code for verification of VIRT-2837
        self.block_data = self.server_behaviors.create_block_device_mapping_v1_virt2837(
            device_name="SSD",
            volume_id=self.bootable_volume_ref,
            delete_on_termination=True)
        # Try Creating Instance from Volume V1
        with self.assertRaises(BadRequest):
            self.boot_from_volume_client.create_server_virt2837(
                block_device_mapping_v1=self.block_data,
                flavor_ref=self.flavors_config.primary_flavor,
                name=rand_name("server"))