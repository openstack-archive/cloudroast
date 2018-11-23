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
from cloudcafe.networking.networks.common.constants import NeutronResponseCodes
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class TestVirtualInterfaceList(NetworkingComputeFixture):
    """
    Test Module for the os_interfacesv2 virtual interface list service
    """
    NAMES_PREFIX = "virtual_interface"

    @tags('positive')
    def test_server_with_one_isolated_network(self):
        """
        Testing a server that only has an isolated network
        """
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [network.id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(1, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_one_public_network(self):
        """
        Testing a server that only has a public network
        """
        network_ids = [self.public_network_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(1, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_one_private_network(self):
        """Testing a server that only has a private network"""
        network_ids = [self.service_network_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(1, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_iso_and_public(self):
        """
        Testing a server with isolated and public networks
        """
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [network.id, self.public_network_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(2, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_iso_and_private(self):
        """
        Testing a server with isolated and private networks
        """
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [network.id, self.service_network_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(2, len(interfaces_list),
                         'Unexpected interface response')

    @tags('smoke', 'positive')
    def test_server_with_iso_public_and_private(self):
        """
        Testing a server with isolated, public and private networks
        """
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [network.id, self.service_network_id,
                       self.public_network_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(3, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_public_and_private(self):
        """
        Testing a server with public and private networks
        """
        network_ids = [self.service_network_id, self.public_network_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(2, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_zserver_with_eight_isolated(self):
        """
        Testing a server with 8 isolated networks
        """
        required_networks = 8
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(8, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_seven_isolated_and_public(self):
        """
        Testing a server with 7 isolated and public networks
        """
        required_networks = 7
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
        network_ids.append(self.public_network_id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(8, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_seven_isolated_and_private(self):
        """
        Testing a server with 7 isolated and private networks
        """
        required_networks = 7
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
        network_ids.append(self.service_network_id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(8, len(interfaces_list),
                         'Unexpected interface response')

    @tags('positive')
    def test_server_with_six_iso_public_and_private(self):
        """
        Testing a server with  isolated, public and private networks
        """
        required_networks = 6
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
        network_ids.append(self.public_network_id)
        network_ids.append(self.service_network_id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server.id)
        interfaces_list = interfaces.entity
        # check the virtual interface list call was done OK
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
            'Unable to get Virtual Interfaces')
        # check the virtual interfaces match the number of networks
        self.assertEqual(8, len(interfaces_list),
                         'Unexpected interface response')

    @tags('negative')
    def test_inexisting_server(self):
        """
        Negative test, Testing with a server that does not exists
        """
        interfaces = self.compute.servers.client.list_virtual_interfaces(
            'inexisting-server-id-8dc3f73ec851')
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.NOT_FOUND,
            'Unexpected HTTP status code on response')
        self.assertIsNone(interfaces.entity, 'Unexpected entity data')

        # testing with a missing server id
        interfaces = self.compute.servers.client.list_virtual_interfaces('')
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.NOT_FOUND,
            'Unexpected HTTP status code on response')
        self.assertIsNone(interfaces.entity, 'Unexpected entity data')
