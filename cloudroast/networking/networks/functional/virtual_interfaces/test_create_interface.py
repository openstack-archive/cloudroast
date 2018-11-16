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
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class TestCreateInterface(NetworkingComputeFixture):
    NAMES_PREFIX = "virtual_interface"

    @tags('smoke', 'positive')
    def test_add_public_network_interface_with_isolated(self):
        """
        Add public interface to server with only isolated network.
        """
        public_id = self.public_network_id
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

        response = self.compute.servers.client.create_virtual_interface(
            server.id, public_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching public {2} network interface at server {3}')\
            .format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                    public_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)
        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with isolated, and public {3} networks'). \
            format(len(interface_list), 2, server.id, public_id)
        self.assertEquals(len(interface_list), 2, msg)

    @tags('positive')
    def test_add_public_network_interface_with_private(self):
        """
        Add public interface to server with only private network.
        """
        public_id = self.public_network_id
        private_id = self.service_network_id
        network_ids = [private_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, public_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching public {2} network interface at server {3}')\
            .format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                    public_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)
        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with private, and public {3} networks'). \
            format(len(interface_list), 2, server.id, public_id)
        self.assertEquals(len(interface_list), 2, msg)

    @tags('smoke', 'positive')
    def test_add_private_network_interface_with_isolated(self):
        """
        Add private interface to server with only isolated network.
        """
        private_id = self.service_network_id
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

        response = self.compute.servers.client.create_virtual_interface(
            server.id, private_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching private {2} network interface at server {3}')\
            .format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                    private_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)
        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with isolated, and private {3} networks'). \
            format(len(interface_list), 2, server.id, private_id)
        self.assertEquals(len(interface_list), 2, msg)

    @tags('smoke', 'positive')
    def test_add_private_network_interface_with_public(self):
        """
        Add private interface to server with only public network.
        """
        private_id = self.service_network_id
        public_id = self.public_network_id
        network_ids = [public_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, private_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching private {2} network interface at server {3}')\
            .format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                    private_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)
        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with public, and private {3} networks'). \
            format(len(interface_list), 2, server.id, private_id)
        self.assertEquals(len(interface_list), 2, msg)

    @tags('smoke', 'positive')
    def test_add_isolated_network_interface_with_public(self):
        """
        Add isolated interface to server with only public network.
        """
        public_id = self.public_network_id
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        network_ids = [public_id]
        self.delete_networks.append(network.id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, network.id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching isolated {2} network interface at server {3}')\
            .format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                    network.id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)
        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with public, and isolated {3} networks'). \
            format(len(interface_list), 2, server.id, network.id)
        self.assertEquals(len(interface_list), 2, msg)

    @tags('positive')
    def test_add_isolated_network_interface_with_private(self):
        """
        Add isolated interface to server with only private network.
        """
        private_id = self.service_network_id
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        network_ids = [private_id]
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, network.id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching isolated {2} network interface at server {3}')\
            .format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                    network.id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)
        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with private, and isolated {3} networks'). \
            format(len(interface_list), 2, server.id, network.id)
        self.assertEquals(len(interface_list), 2, msg)

    @tags('smoke', 'positive')
    def test_add_isolated_network_interface_with_public_and_private(self):
        """
        Add isolated interface to server with public and private networks
        """
        public_id = self.public_network_id
        private_id = self.service_network_id
        network_ids = [public_id, private_id]
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        self.delete_networks.append(network.id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with Public and Private networks').\
            format(len(interface_list), 2, server.id)
        self.assertEquals(len(interface_list), 2, msg)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, network.id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching isolated {2} network interface at server {3}').\
            format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                   network.id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with Public, Private, and isolated {3} networks').\
            format(len(interface_list), 3, server.id, network.id)
        self.assertEquals(len(interface_list), 3, msg)

    @tags('positive')
    def test_add_public_network_interface_with_isolated_and_private(self):
        """
        Add public interface to server with isolated and private network.
        """
        public_id = self.public_network_id
        private_id = self.service_network_id
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        network_ids = [network.id, private_id]
        self.delete_networks.append(network.id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with Isolated and Private networks').\
            format(len(interface_list), 2, server.id)
        self.assertEquals(len(interface_list), 2, msg)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, public_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching public {2} network interface at server {3}').\
            format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                   public_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with Private, isolated, and public {3} networks').\
            format(len(interface_list), 3, server.id, public_id)
        self.assertEquals(len(interface_list), 3, msg)

    @tags('positive')
    def test_add_private_network_interface_with_isolated_and_public(self):
        """
        Add private interface to server with isolated and public network.
        """
        public_id = self.public_network_id
        private_id = self.service_network_id
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        network_ids = [network.id, public_id]
        self.delete_networks.append(network.id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with Public and Isolated networks').\
            format(len(interface_list), 2, server.id)
        self.assertEquals(len(interface_list), 2, msg)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, private_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching private {2} network interface at server {3}').\
            format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                   private_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with isolated, public, and private {3} networks').\
            format(len(interface_list), 3, server.id, private_id)
        self.assertEquals(len(interface_list), 3, msg)

    @tags('positive')
    def test_add_isolated_network_interface_with_five_networks(self):
        """
        Add isolated interface to server with 5 networks, public, and private
        """
        public_id = self.public_network_id
        private_id = self.service_network_id
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        isolated_network = self.create_server_network(name=network_name, ipv4=True)
        required_networks = 5
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
        network_ids.append(public_id)
        network_ids.append(private_id)
        self.delete_networks.extend(network_ids)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, isolated_network.id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching isolated {2} network interface at server {3}').\
            format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                   isolated_network.id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with private, public, and isolated {3} networks').\
            format(len(interface_list), 8, server.id, isolated_network.id)
        self.assertEquals(len(interface_list), 8, msg)

    @tags('positive')
    def test_add_private_network_interface_with_six_networks(self):
        """
        Add private interface to server with 6 networks and public
        """
        public_id = self.public_network_id
        private_id = self.service_network_id
        required_networks = 6
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
        network_ids.append(public_id)
        self.delete_networks.extend(network_ids)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, private_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching private {2} network interface at server {3}').\
            format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                   private_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with isolated, public, and private {3} networks').\
            format(len(interface_list), 8, server.id, private_id)
        self.assertEquals(len(interface_list), 8, msg)

    @tags('positive')
    def test_add_public_network_interface_with_six_networks(self):
        """
        Add public interface to server with 6 networks and private
        """
        public_id = self.public_network_id
        private_id = self.service_network_id
        required_networks = 6
        network_ids = []
        for i in range(1, required_networks+1):
            network_name = 'network_{}_{i}'.format(self.NAMES_PREFIX, i=i)
            network = self.create_server_network(name=network_name, ipv4=True)
            network_ids.append(network.id)
        network_ids.append(private_id)
        self.delete_networks.extend(network_ids)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, public_id)
        msg = ('Unexpected Virtual Interface Create Response HTTP {0} instead '
               'of HTTP {1} attaching public {2} network interface at server {3}').\
            format(response.status_code, NeutronResponseCodes.CREATE_INTERFACE,
                   public_id, server.id)
        self.assertEquals(response.status_code,
                          NeutronResponseCodes.CREATE_INTERFACE, msg)

        response = self.compute.servers.client.list_virtual_interfaces(server.id)
        interface_list = response.entity
        msg = ('Unexpected Virtual Interface Count {0} instead of {1}. '
               'Expecting server {2} with isolated, private, and public {3} networks').\
            format(len(interface_list), 8, server.id, private_id)
        self.assertEquals(len(interface_list), 8, msg)

    @tags('negative')
    def test_add_existing_interfaces(self):
        public_id = self.public_network_id
        private_id = self.service_network_id
        network_name = 'network_{0}'.format(self.NAMES_PREFIX)
        network = self.create_server_network(name=network_name, ipv4=True)
        network_ids = [public_id, private_id, network.id]
        self.delete_networks.append(network.id)
        keypair_name = 'key_{0}'.format(self.NAMES_PREFIX)
        keypair = self.create_keypair(name=keypair_name)
        self.delete_keypairs.append(keypair.name)
        svr_name = 'svr_{0}'.format(self.NAMES_PREFIX)
        server = self.create_test_server(
            name=svr_name, key_name=keypair.name,
            network_ids=network_ids, active_server=True)
        self.delete_servers.append(server.id)

        response = self.compute.servers.client.create_virtual_interface(
            server.id, public_id)
        self.assertEquals(response.status_code, 400,
                          'Existing public interface was allowed to be added')

        response = self.compute.servers.client.create_virtual_interface(
            server.id, private_id)
        self.assertEquals(response.status_code, 400,
                          'Existing private interface was allowed to be added')

        response = self.compute.servers.client.create_virtual_interface(
            server.id, network.id)
        self.assertEquals(response.status_code, 400,
                          'Existing isolated interface was allowed to be added')
