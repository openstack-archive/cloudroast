"""
Copyright 2018 Rackspace

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
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudroast.compute.fixtures import ComputeFixture
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class TestServerActions(NetworkingComputeFixture, ComputeFixture):
    NAMES_PREFIX = "actions"

    @tags('positive')
    def test_net_config_rebuild_server_from_snapshot(self):
        """
        Snapshots do not include networks configurations (REBUILD).
        """
        server, isolated_network = self._shared_server(iso_net=False)
        rebuilt_server_response = self.compute.servers.client.rebuild(
            server_id=server.id, name=server.name,
            image_ref=self.image_ref_alt, admin_pass=server.admin_pass)
        self.assertEqual(rebuilt_server_response.status_code, 202,
                         'Server Rebuild status code incorrect')
        self.server_behaviors.wait_for_server_status(
            server.id, NovaServerStatusTypes.ACTIVE)
        rebuilt_server = rebuilt_server_response.entity
        shared_net = rebuilt_server.addresses.get_by_name(
            isolated_network.name)
        self.assertIsNone(shared_net)

    @tags('positive')
    def test_server_rebuild_network_configuration(self):
        """
        Verify network configuration remains after server rebuild.
        """
        server, isolated_network = self._shared_server(iso_net=True)
        rebuilt_server_response = self.compute.servers.client.rebuild(
            server_id=server.id, name=server.name,
            image_ref=self.image_ref_alt, admin_pass=server.admin_pass)
        self.assertEqual(rebuilt_server_response.status_code, 202,
                         'Server Rebuild status code incorrect')
        self.server_behaviors.wait_for_server_status(
            server.id, NovaServerStatusTypes.ACTIVE)
        rebuilt_server = rebuilt_server_response.entity
        self.assertIsNotNone(rebuilt_server.addresses.get_by_name(
            isolated_network.name))
        self.assertIsNotNone(rebuilt_server.addresses.public)
        self.assertIsNotNone(rebuilt_server.addresses.private)

    @tags('positive')
    def test_server_resize_network_configuration(self):
        """
        Verify network configuration remains after server resize.
        """
        new_flavor = self.flavor_ref
        if new_flavor == '2':
            new_flavor = '3'
        else:
            new_flavor = '2'
        server, isolated_network = self._shared_server(iso_net=True)
        resize_server_response = self.compute.servers.client.resize(
            server.id, new_flavor)
        self.assertEqual(resize_server_response.status_code, 202,
                         'Server Resize status code is incorrect')
        resize_server_response = self.server_behaviors.wait_for_server_status(
            server.id, NovaServerStatusTypes.VERIFY_RESIZE)
        resize_server_response.entity.admin_pass = server.admin_pass
        resize_server = resize_server_response.entity
        self.assertIsNotNone(resize_server.addresses.get_by_name(
            isolated_network.name))
        self.assertIsNotNone(resize_server.addresses.public)
        self.assertIsNotNone(resize_server.addresses.private)

        confirm_resize_response = self.compute.servers.client.confirm_resize(
            server.id)
        self.assertEqual(confirm_resize_response.status_code, 204,
                         'Confirm Resize status code is incorrect.')
        confirm_resize_response = self.server_behaviors.wait_for_server_status(
            server.id, NovaServerStatusTypes.ACTIVE)
        confirm_resize_response.entity.admin_pass = server.admin_pass
        resize_confirm = confirm_resize_response.entity
        self.assertIsNotNone(resize_confirm.addresses.get_by_name(
            isolated_network.name))
        self.assertIsNotNone(resize_confirm.addresses.public)
        self.assertIsNotNone(resize_confirm.addresses.private)

    @tags('positive')
    def test_rescue_server_maintains_network_connectivity(self):
        """
        Verify network connectivity remains after server rescue.
        """
        server, isolated_network = self._shared_server(iso_net=True)
        rescue_server_response = self.rescue_client.rescue(server.id)
        self.assertEqual(rescue_server_response.status_code, 200,
                         'Rescue server status code incorrect')
        rescue_server_response = self.server_behaviors.wait_for_server_status(
            server.id, NovaServerStatusTypes.RESCUE)
        rescue_server = rescue_server_response.entity
        self.assertIsNotNone(rescue_server.addresses.get_by_name(
            isolated_network.name))
        self.assertIsNotNone(rescue_server.addresses.public)
        self.assertIsNotNone(rescue_server.addresses.private)

        unrescue_response = self.rescue_client.unrescue(server.id)
        self.assertEqual(unrescue_response.status_code, 202,
                         'Unrescue server status code incorrect')
        unrescue_response = self.server_behaviors.wait_for_server_status(
            server.id, NovaServerStatusTypes.ACTIVE)
        unrescue_server = unrescue_response.entity
        self.assertIsNotNone(unrescue_server.addresses.get_by_name(
            isolated_network.name))
        self.assertIsNotNone(unrescue_server.addresses.public)
        self.assertIsNotNone(unrescue_server.addresses.private)

    def _shared_server(self, iso_net=False):
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        isolated_network = self.create_server_network(
            name=network_name, ipv4=True)
        if iso_net:
            network_ids = [self.public_network_id,
                           self.service_network_id,
                           isolated_network.id]
        else:
            network_ids = [self.public_network_id,
                           self.service_network_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)
        return server, isolated_network
