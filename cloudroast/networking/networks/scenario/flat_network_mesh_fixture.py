"""
Copyright 2016 Rackspace

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

import random

from cloudroast.networking.networks.fixtures import NetworkingComputeFixture

from cloudcafe.networking.networks.common.proxy_mgr.proxy_mgr \
    import NetworkProxyMgr
from cloudcafe.networking.networks.personas import ServerPersona

import prettytable


class NetTypes(object):

    # Maps to 'persona attribute' naming convention, built for easier
    # understanding of inet, pnet, snet.
    # REASON: I keep associating inet with internet or linux's
    # "inet" (network interface).

    ISO_NET = 'inet'
    PUBLIC_NET = 'pnet'
    SVC_NET = 'snet'
    ALL_NETWORK_TYPES = [PUBLIC_NET, SVC_NET, ISO_NET]


class MeshedNetworkFixture(NetworkingComputeFixture):

    ADMIN_PASS = 'tst_login_{0:04}'.format(random.randint(1, 9999))

    # NOTE: These should be customized at instantiation, depending on the
    # purpose of the tests associated with the fixture.

    # Number of servers to build as part of the FIXTURE. Tests should build
    # additional servers if they need to test a specific aspect of the VM.
    NUM_TO_BUILD = 3

    # Default pings: The more pings, the longer the mesh validcation takes,
    # but five (5) gives a reasonable initial assessment of any potential
    # connectivity issues.
    DEFAULT_PING_COUNT = 5

    SSH = 'ssh'
    PING = 'ping'

    PROXY = 'proxy'
    PERSONA = 'persona'
    SERVER = 'server'

    @classmethod
    def setUpClass(cls):
        super(MeshedNetworkFixture, cls).setUpClass()

        # Attributes registered here, populated in setUp()
        cls.iso_net = None
        cls.iso_net_gw = None

        # dictionary key = server_id
        cls.servers = {}

        # For each network type, this will contain the textual prettytable
        # representation of the results (connectivity between each host)
        # dictionary key = network type (as defined in NetTypes class)
        cls.last_connectivity_check = {}

    def setUp(self):
        super(MeshedNetworkFixture, self).setUp()

        # Since tests can impact the meshed network setup, the first time setup
        # is called, it will build each server. If any test changes a server,
        # the server should deleted: NOTE: USE THE FIXTURE'S
        # delete_registered_server(), as this will update the bookkeeping
        # required to maintain the mesh configuration. The next test will
        # verify that all servers are available, and rebuild any that have
        # been removed.

        # Need to define an isolated net to share with multiple servers
        if self.iso_net is None:
            self.log_action('Building Common ISOLATED network')
            self.iso_network, _, self.iso_net_gw = \
                self._build_isolated_network()

        # Verify/build NUM_TO_BUILD servers attached to the same isolated net
        self.log_action(
            'Checking and building the meshed server configuration '
            '(Num_svrs={0})'.format(self.NUM_TO_BUILD))

        num_to_build = 0
        if len(self.servers.keys()) < self.NUM_TO_BUILD:
            num_to_build = self.NUM_TO_BUILD - len(self.servers.keys())

        for num in xrange(num_to_build):
            svr_num = num + len(self.servers.keys())
            self.fixture_log.debug('Building server number: {0}'.format(
                svr_num))
            self._build_and_register_iso_net_server(
                svr_id_num=svr_num, iso_network=self.iso_network)

        # Verify initial connectivity
        connectivity = self.verify_ping_connectivity(
            ping_count=self.DEFAULT_PING_COUNT)
        if not connectivity:
            self.assertClassSetupFailure(
                'Servers do not have full connectivity. See logs for details.')

    def delete_registered_server(self, server_id):
        """
        Deletes server and removes it from the list of personas and proxy_mgrs

        :param server_id: ID of server to delete and remove from tracking.

        :return: True (No validation at this point)

        """
        if server_id not in self.servers:
            self.fixture_log.error(
                'Cannot delete server. Unable to find registered server with '
                'id: {id}'.format(id=server_id))
            return False

        self.compute.servers.client.delete_server(server_id)
        self.compute.servers.behaviors.wait_for_server_to_be_deleted(
            server_id=server_id)

        del self.servers[server_id]

        return True

    def verify_ping_connectivity(self, ping_count=5):
        """
        Verify connectivity across network mesh using ping
        :param ping_count: Number of pings to use between each server

        :return: (Boolean) - Full connectivity was detected
        """
        return self._verify_action_connectivity(
            method=self.PING, ping_count=ping_count)

    def verify_ssh_connectivity(self):
        """
        Verify connectivity across network mesh using ssh (via logging in
        and issuing basic command) - Only supports Linux at this point. (See
        NetworkProxyMgr for more information)

        :return: (Boolean) - Full connectivity was detected
        """
        return self._verify_action_connectivity(method=self.SSH)

    def _verify_action_connectivity(self, method, **kwargs):
        """
        Verify network connectivity using the provided method. (Currently
        supports ping and SSH only).

        This routine does the bean counting, but leverages the corresponding
        <action>_net_mesh_() command to do the actual action.

        :param method: Mechanism used to determine connectivity.
        :param kwargs: Any extra args required by mechanism. These are defined
           by the wrapper functions (e.g. - verify_ping_connectivity())

        :return: (Boolean) - Full connectivity was detected
        """
        full_network_conn = True

        # Determine which <action>_net_mesh() API to call
        method == self.SSH if self.SSH in method.lower() else self.PING
        api_name = '{0}_net_mesh'.format(method)
        api = getattr(self, api_name)

        # For each type of network
        for net_type in NetTypes.ALL_NETWORK_TYPES:
            svr_conn, results_table = api(
                servers=self.servers, net_type=net_type, **kwargs)
            result_msg = '\n{table!s}'.format(table=results_table)

            self.fixture_log.info(result_msg)
            self.last_connectivity_check[net_type] = result_msg

            # svr_conn is None if there is a single server
            if svr_conn is not None:
                full_network_conn = full_network_conn & svr_conn
        return full_network_conn

    def _build_and_register_iso_net_server(self, svr_id_num, iso_network):
        """
        Builds and registers a server that is attached to the specified
        isolated network.

        :param svr_id_num: Number of server (used in server naming only)
        :param iso_network: Network Obj representing the iso_network

        :return: server id of newly created/registered server

        """
        network_ids = [self.public_network_id, self.service_network_id,
                       iso_network.id]
        svr_name = 'isonet_test_server_{0}'.format(svr_id_num)

        # Build the server
        server_resp = self.net.behaviors.create_networking_server(
            name=svr_name, network_ids=network_ids, admin_pass=self.ADMIN_PASS)
        server = server_resp.entity
        setattr(server, 'admin_pass', self.ADMIN_PASS)

        # Register the server (using the server id)
        self.servers[server.id] = {}
        self.servers[server.id][self.SERVER] = server

        # Make sure server is registered to be cleaned up...
        if server.id not in self.delete_servers:
            self.delete_servers.append(server.id)

        # Build a network persona for the server (stored by server_id)
        self.servers[server.id][self.PERSONA] = ServerPersona(
            server=server, network=iso_network, inet_fix_ipv4_count=1,
            inet=True)
        self.fixture_log.debug(self.servers[server.id][self.PERSONA])

        # Build a proxy_mgr (allows easy access to the server to execute
        # commands from that server) - stored by server_id.
        proxy = NetworkProxyMgr(use_proxy=True)
        proxy.set_proxy_server(server)
        self.servers[server.id][self.PROXY] = proxy

        return server.id

    def ssh_net_mesh(self, servers, net_type, username=None, password=None):
        """
        SSH from each host to every other host contained in the personas.

        :param servers: Dictionary of server information (server, proxy,
                persona)
        :param net_type: Type of network to validate (types defined in
            NetTypes class)
        :param username: The username required for log in. (Assumes all
            servers have a common user/password)
        :param password: The password required for log in. (Assumes all
            servers have a common user/password)

        :return: (Boolean) Full SSH connectivity on the specified network

        """
        action = self.SSH
        return self._action_on_net_mesh(
            servers=servers, net_type=net_type, action=action,
            username=username, password=password)

    def ping_net_mesh(self, servers,  net_type, ip_version=4, threshold=1,
                      ping_count=DEFAULT_PING_COUNT):
        """
        Ping from each host to every other host contained in the personas.

        :param servers: Dictionary of server information (server, proxy,
                persona)
        :param net_type: Type of network to validate (types defined in
            NetTypes class)
        :param ip_version: IP Version to use (4|6)
        :param ping_count: Number of pings to use...
        :param threshold: Number of pings responses required to indicate
            successful network connectivity

        :return: (Boolean) Full ping connectivity on the specified network
        """
        action = self.PING
        return self._action_on_net_mesh(
            servers=servers, net_type=net_type, action=action,
            threshold=threshold, ping_count=ping_count, ip_version=ip_version)

    def _action_on_net_mesh(self, servers, net_type, action, ip_version=4,
                            **kwargs):
        """
        Performs specified action to verify network connectivity on
        specified network. Stores results in a table for full reporting.

        :param servers: Dictionary of server information (server, proxy,
                persona)
        :param net_type: Type of network to validate (types defined in
            NetTypes class)
        :param action: Type of mechanism to validate connectivity
        :param ip_version: IP Version (4|6)
        :param kwargs: Any extra arguments required for the validation
        mechanism. These should be specified by the various wrapper
        functions, and will be passed on to the proxy_args generator.

        :return: (tuple) [boolean] Results, [prettyTable} Table of actions
            and results.
        """

        # Change the action to match the proxy api_name
        if self.SSH in action.lower():
            action = 'can_{0}'.format(self.SSH)

        # Determine relevant presona attribute to use
        network_attr = '{net_type}_fix_ipv{version}'.format(
            net_type=net_type, version=ip_version)

        # Get list of addresses in mesh based on network and ip version
        # Get list of server ids for each server in mesh...
        result_msg = "{src} --> {dest} : {result}"
        overall_result = None

        # Define the stable structure
        table_header = ['{action}: {net_type}'.format(
            net_type=net_type.upper(), action=action.upper())]
        table_rows = []

        svr_ids = servers.keys()

        # Iterate across selected ip addresses in mesh
        for svr_id in svr_ids:

            # Get source server info
            proxy = servers[svr_id][self.PROXY]
            persona = servers[svr_id][self.PERSONA]
            src_ip = getattr(persona, network_attr)[0]
            row_data = [src_ip]

            # Get the requested proxy action API (ping, can_ssh)
            action_api = getattr(proxy, action)

            for target_svr_id in svr_ids:

                target_ip = getattr(
                    servers[target_svr_id][self.PERSONA], network_attr)[0]

                if target_ip not in table_header:
                    table_header.append(target_ip)

                # Build the correct api signature based on the action and any
                # extra relevant parameters provided
                action_api_args = self._build_proxy_api_args(
                    action=action, target_ip=target_ip, **kwargs)

                # If the target current server is not the source server
                if target_svr_id != svr_id:
                    try:
                        result = action_api(**action_api_args)

                    # Oops, something didn't work... (e.g. SSH timeout)
                    except Exception as err:
                        result = False
                        msg = 'ERROR: {0}'.format(err)
                        row_data.append(msg)
                        self.fixture_log.error(msg)

                    # Able to execute command, so store result to put into
                    # the table
                    else:
                        row_data.append(result)
                        msg = result_msg.format(
                            src=src_ip, dest=target_ip,
                            result=result)
                        self.fixture_log.info(msg)

                    # Accumulate the logical result
                    overall_result = (
                        result if overall_result is None else
                        overall_result & result)

                # No need for the source host to ping itself.
                else:
                    row_data.append('---')

            # Store results from source host
            table_rows.append(row_data)

        # Add results for given source host to table
        result_table = prettytable.PrettyTable(table_header)
        [result_table.add_row(row) for row in table_rows]

        return overall_result, result_table

    def _build_proxy_api_args(self, action, target_ip, **kwargs):
        """
        Builds basic proxy args (tightly coupled with NetworkProxy class)

        :param action: ping or ssh
        :param target_ip: IP address to target action toward
        :param address_pool: pool of target  addresses to verify connectivity
        :param kwargs: extra action args required for specific proxy commands

        :return: dictionary of arguments for setting up proxy agent

        """
        # Every action requires a target IP
        args_dict = {'target_ip': target_ip}

        additional_args = {}
        # Build SSH proxy args
        if self.SSH in action.lower():
            additional_args = {
                'user': kwargs.get('username', NetworkProxyMgr.DEFAULT_USER),
                'password': kwargs.get('password', self.ADMIN_PASS)}

        # Build ping proxy args
        elif self.PING in action.lower():
            additional_args = {
                'count': kwargs.get('ping_count', self.DEFAULT_PING_COUNT),
                'ip_version': kwargs.get('ip_version', 4),
                'threshold': kwargs.get('threshold', 1)}

        # Add any additional args to the proxy args
        args_dict.update(additional_args)
        return args_dict

    def _build_isolated_network(self, ip_version=4):
        """
        Build a network and subnet with allocation pools

        :param ip_version: (int) 4|6 --> IPv4/IPv6

        :return: (tuple) network object, subnet obj, gateway ip

        """
        # Create the network
        network = self.create_network()

        # Build an isolated network
        create_iso_net_api = self.net.subnets.behaviors.create_ipv4_cidr
        net_mask_suffix = 'ipv{ver}_suffix'.format(ver=ip_version)
        subnet_mask_bits = 24
        if ip_version == 6:
            create_iso_net_api = self.net.subnets.behaviors.create_ipv6_cidr
            subnet_mask_bits = 8

        # Build address range for subnet
        create_network_args = {net_mask_suffix: subnet_mask_bits}
        isolated_net = create_iso_net_api(**create_network_args)

        # Define allocation pools and network gateway
        # NOTE: Network gateway is configured to always be x.x.x.1,
        # host addresses start at x.x.x.2
        allocation_pool = self.net.subnets.behaviors.get_allocation_pool(
            cidr=isolated_net, start_increment=2, end_increment=100)
        gateway_ip = self.net.subnets.behaviors.get_next_ip(
            isolated_net, num=1)

        # Create corresponding subnet
        subnet = self.net.subnets.behaviors.create_subnet(
            network_id=network.id, ip_version=ip_version, cidr=isolated_net,
            gateway_ip=gateway_ip, allocation_pools=[allocation_pool])

        return network, subnet, gateway_ip

    def log_action(self, msg):
        """
        Logs info_level msg that indicates what the current step is performing.
        This is a helper function to make steps more clearly marked in the log
        file. (Surrounded by border)

        :param msg: (str) Msg describing action.

        :return: None

        """
        length = len(msg) + 10 if len(msg) > 70 else 80
        border = '*' * length
        log_fmt = (
            '\n+{{border}}+\n|{{msg:^{length}}}|\n+{{border}}+\n'.format(
                length=length))
        log_msg = log_fmt.format(border=border, msg=msg)
        self.fixture_log.info(log_msg)
