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
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class TestVirtualInterfaceDelete(NetworkingComputeFixture):
    """
    Test Module for the os_interfacesv2 virtual interface delete service
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
        vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_one_public_network(self):
        """
        Testing a server that only has a public network
        """
        vi_delete_type = 'public'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_one_private_network(self):
        """Testing a server that only has a private network"""
        vi_delete_type = 'private'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_iso_and_public(self):
        """
        Testing a server with isolated and public networks
        """
        vi_delete_type = 'public'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_iso_and_public_b(self):
        """
        Testing a server with isolated and public networks
        """
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [network.id, self.public_network_id]
        vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_iso_and_private(self):
        """
        Testing a server with isolated and private networks
        """
        vi_delete_type = 'private'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_iso_and_private_b(self):
        """
        Testing a server with isolated and private networks
        """
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [network.id, self.service_network_id]
        vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('smoke', 'positive', 'identity')
    def test_server_with_iso_public_and_private(self):
        """
        Testing deleting ServiceNet VIF
        """
        vi_delete_type = 'private'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('smoke', 'positive')
    def test_server_with_iso_public_and_private_b(self):
        """
        Testing deleting Public VIF
        """
        vi_delete_type = 'public'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('smoke', 'positive')
    def test_server_with_iso_public_and_private_c(self):
        """
        Testing deleting Isolated VIF
        """
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [network.id, self.service_network_id,
                       self.public_network_id]
        vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_public_and_private(self):
        """
        Testing a server with public and private networks
        """
        vi_delete_type = 'public'
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [self.service_network_id,
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
        self.assertEqual(2, len(interfaces_list),
                         'Unexpected interface response')
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_public_and_private_b(self):
        """
        Testing a server with public and private networks
        """
        vi_delete_type = 'private'
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        network_ids = [self.service_network_id,
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
        self.assertEqual(2, len(interfaces_list),
                         'Unexpected interface response')
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

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
            if i == 1:
                vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

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
        vi_delete_type = 'public'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_seven_isolated_and_public_b(self):
        """
        Testing a server with 7 isolated and public networks
        """
        required_networks = 7
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
            if i == 1:
                vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

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
        vi_delete_type = 'private'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_seven_isolated_and_private_b(self):
        """
        Testing a server with 7 isolated and private networks
        """
        required_networks = 7
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
            if i == 1:
                vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

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
        vi_delete_type = 'public'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_six_iso_public_and_private_b(self):
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
        vi_delete_type = 'private'
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('positive')
    def test_server_with_six_iso_public_and_private_c(self):
        """
        Testing a server with  isolated, public and private networks
        """
        required_networks = 6
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
            if i == 1:
                vi_delete_type = network.name
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
        # delete the virtual interface
        vi_to_delete = self._get_vi_id(interfaces_list, vi_delete_type)
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        self.assertEqual(response.status_code,
                         NeutronResponseCodes.DELETE_INTERFACE,
                         'Unable to delete virtual interface')
        self._check_virtual_interface_delete(server.id, interfaces_list,
                                             vi_to_delete)

    @tags('negative')
    def test_inexisting_server(self):
        """
        Negative test, Testing with a server that does not exists
        """
        server_id = 'inexisting-server-id-8dc3f73ec851'
        interfaces = self.compute.servers.client.list_virtual_interfaces(
            server_id)
        self.assertEqual(
            interfaces.status_code, NeutronResponseCodes.NOT_FOUND,
            'Unexpected HTTP status code on response')
        self.assertIsNone(interfaces.entity, 'Unexpected entity data')
        # delete the virtual interface
        vi_to_delete = 'inexisting-virtual-interface'
        response = self.compute.servers.client.delete_virtual_interface(
                                                    server_id, vi_to_delete)
        # check the delete call returns an Internal Server Error, 404 status
        msg = 'Expected {} HTTP response but received {} HTTP response'.format(
            NeutronResponseCodes.NOT_FOUND, response.status_code)
        self.assertEqual(
            response.status_code, NeutronResponseCodes.NOT_FOUND,
            msg=msg)

    @tags('negative')
    def test_with_incorrect_data(self):
        """
        Negative test, Testing with incorrect virtual interface ids
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
        # try to delete virtual interface with invalid network id
        vi_to_delete = network.name + "-invalid-net-id"
        response = self.compute.servers.client.delete_virtual_interface(
            server.id, vi_to_delete)
        # check the delete call returns 200 status code
        msg = 'Expected {} HTTP response but received {} HTTP response'.format(
            NeutronResponseCodes.DELETE_INTERFACE, response.status_code)
        self.assertEqual(
            response.status_code, NeutronResponseCodes.DELETE_INTERFACE,
            msg=msg)
        # Again check list of virtual interfaces to make sure valid interface
        # is not deleted
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

    def _get_vi_id(self, interfaces_list, vi_delete_type):
        """
        Provides the Virtual Interface ID of a network type
        """
        for interface in interfaces_list:
            if interface.network_label == vi_delete_type:
                return interface.id

    def _check_virtual_interface_delete(self, server_id,
                                        net_list, vi_to_delete,
                                        interval_time=7, timeout=None):
        """
        Checks that the Virtual Interface was deleted
        """
        timeout = timeout or 100
        time_count = 0
        msg = 'Unable to get virtual interfaces from server {0}'
        while time_count <= timeout:
            # check the interface was deleted from the server
            interfaces = self.compute.servers.client.list_virtual_interfaces(
                server_id)
            interfaces_list = interfaces.entity
            self.assertEqual(
                interfaces.status_code, NeutronResponseCodes.LIST_INTERFACES,
                msg.format(server_id))
            if len(net_list)-1 == len(interfaces_list):
                break
            time.sleep(interval_time)
            time_count += interval_time
        vmsg = ('Expected {0} instead of {1} virtual interfaces at server '
                '{2}').format(len(net_list)-1, len(interfaces_list), server_id)
        self.assertEqual(len(net_list)-1, len(interfaces_list), vmsg)
        for i in range(len(interfaces_list)):
            self.assertNotEqual(interfaces_list[i].id, vi_to_delete)
