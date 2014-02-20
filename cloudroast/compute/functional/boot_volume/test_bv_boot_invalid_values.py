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
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.blockstorage.config import BlockStorageConfig
from cloudroast.compute.fixtures import ComputeFixture


class BootInvalidValues(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(BootInvalidValues, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)

    @tags(type='smoke', net='yes')
    @unittest.skip("Known issue")
    def test_for_invalid_device_name_should_not_be_created(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        self.err_msg=""
        try:
            # NDN = Negative Device Name
            self.trigger_value = "NDN"
            self.response, self.volume_id = self.server_behaviors.boot_volume(
                self.key, self.trigger_value)
        except Exception as self.err_msg:
            pass
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.assertEqual(self.err_msg, "", self.err_msg)

    @tags(type='smoke', net='yes')
    @unittest.skip("Known issue")
    def test_for_invalid_type_value_should_not_be_created(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        self.err_msg=""
        try:
            # NDN = Negative Type Value
            self.trigger_value = "NTV"
            self.response, self.volume_id = self.server_behaviors.boot_volume(
                self.key, self.trigger_value)
        except Exception as self.err_msg:
            pass
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id, self.servers_client.delete_server)
        self.assertNotEqual(self.err_msg,"","Server built (should not have been built)",)

    @tags(type='smoke', net='yes')
    @unittest.skip("Known issue")
    def test_for_invalid_del_on_term_should_not_be_created(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        self.err_msg=""
        try:
            # NDN = Negative Delete on Termination
            self.trigger_value = "NDOT"
            self.response, self.volume_id = self.server_behaviors.boot_volume(
                self.key, self.trigger_value)
        except Exception as self.err_msg:
            pass
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id, self.servers_client.delete_server)
        self.assertEqual(self.err_msg, "", self.err_msg)

    @tags(type='smoke', net='yes')
    def test_for_invalid_volume_id_should_not_be_created(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        self.err_msg = ""
        try:
            # NDN = Negative Volume ID
            self.trigger_value = "NVI"
            self.response, self.volume_id = self.server_behaviors.boot_volume(
                self.key, self.trigger_value)
        except Exception as self.err_msg:
            pass
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.assertNotEqual(self.err_msg, "",
                            "Server built (should not have been built)")

    @tags(type='smoke', net='yes')
    def test_for_invalid_flavor_should_not_be_created(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        self.err_msg = ""
        try:
            # NDN = Negative Flavor Value
            self.trigger_value = "NFV"
            self.response, self.volume_id = self.server_behaviors.boot_volume(
                self.key, self.trigger_value)
        except Exception as self.err_msg:
            pass
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.assertNotEqual(self.err_msg, "",
                            "Server built (should not have been built)")

    @tags(type='smoke', net='yes')
    def test_for_deleted_volume_should_not_be_created(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        self.err_msg = ""
        try:
            # NDN = Negative Flavor Value
            self.trigger_value = "NDV"
            self.response, self.volume_id = self.server_behaviors.boot_volume(
                self.key, self.trigger_value)
        except Exception as self.err_msg:
            pass
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.assertNotEqual(self.err_msg, "",
                            "Server built (should not have been built)")
