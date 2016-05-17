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
import time

from cloudcafe.networking.networks.common.proxy_mgr.proxy_mgr \
    import NetworkProxyMgr
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.topologies.topology_routines \
    import TopologyFixtureRoutines


class SpokeAndHubFixture(NetworkingComputeFixture, TopologyFixtureRoutines):

    NUM_OF_SPOKES = 5
    IP_VERSION = 4
    SSH_PROVISION_DELAY = 20

    @classmethod
    def setUpClass(cls):
        super(SpokeAndHubFixture, cls).setUpClass()

        cls.iso_nets = []
        cls.iso_subnets = []

        # dictionary key = server_id
        # Sub-dictionary key constants are defined in the
        # TopologyFixtureRoutine class
        # Dictionary Structure:
        #   <server_id>: {PERSONA: <persona_obj>,
        #                 SERVER: <server_model>,
        #                 PROXY: <proxy_model>}
        cls.servers = {}

        # Hub is a single server model representing the hub of the wheel
        # (Every network gateway interface is defined on the hub, and all
        # traffic goes through the hub). Dictionary is same as sub-dictionary
        # in servers. (KEYS = PERSONA, SERVER, PROXY)
        cls.hub = {}

        cls.last_connectivity_check = {}
        cls.base_iso_net = cls.net.subnets.config.ipv4_prefix.replace('*', '0')
        cls.base_iso_subnet_mask = cls.determine_octet_mask(cls.base_iso_net)

    def setUp(self):
        super(SpokeAndHubFixture, self).setUp()

        # If the hub is not defined, build the topology
        if not self.hub.keys():
            self.fixture_log.debug("NUMBER OF SPOKES ON HUB: {0}".format(
                self.NUM_OF_SPOKES))

            self.log_action('Build spoke and hub topology')
            self.servers, self.iso_nets, self.iso_subnets = \
                self._build_spokes()
            self.hub = self._build_hub_router(network_spokes=self.iso_subnets)

            self.log_action('Verify Spoke and Hub Connectivity')
            connectivity = self.verify_ping_connectivity()

            # If DEBUGGING or STAGING FOR MANUAL DEBUGGING
            # (NUM_OF_SPOKES=1), then execute cmd else make sure connectivity
            # is working...
            if self.DEBUG and (not connectivity or self.NUM_OF_SPOKES == 1):
                self.debug_topology_routine()

            # If NUM_OF_SPOKES == 1, recommend using flat network fixture
            elif self.NUM_OF_SPOKES > 1:
                self.assertTrue(connectivity, self.connectivity_error())

    def _build_spokes(self):
        """
        Builds each spoke network (isolated network) and adds a host at
        the end of each spoke. Each network gateway will be registered on
        the hub router.

        :return: (tuple), servers [Dict: end of spoke hosts],
                          iso_nets [List: isolated networks created]
                          iso_subnets [list: isolated network subnets created]
        """
        # NOTE: Each spoke is a subnet on its own isolated network

        # Check to see if any spokes are needed
        if len(self.servers) >= self.NUM_OF_SPOKES:
            return self.servers, self.iso_nets, self.iso_subnets

        # Determine the network needed for the static route
        network_for_static_route = '{net}/{snm}'.format(
            net=self.base_iso_net, snm=self.base_iso_subnet_mask)
        self.fixture_log.info('Network for static route: {0}'.format(
            network_for_static_route))

        # Determine how many spokes are needed and build the spokes
        num_of_spokes = self.NUM_OF_SPOKES - len(self.servers)
        for spoke in xrange(num_of_spokes):
            svr_num = '{run_id!s}_{index!s}'.format(
                index=spoke + len(self.servers), run_id=self.RUN_ID)
            iso_net, iso_subnet, _ = self._build_isolated_network(
                ip_version=self.IP_VERSION)

            # Store ISOLATED Network/Subnet information
            self.iso_nets.append(iso_net)
            self.iso_subnets.append(iso_subnet)

            # Build "End of the spoke" (non-hub) hosts
            self._build_and_register_iso_net_server(
                svr_id_num=svr_num, iso_network=iso_net)

        # Wait for final spoke server to stabilize
        time.sleep(self.SSH_PROVISION_DELAY)

        # Add the generalized isolated network static route (so any isolated
        # subnets are routed out the local isolated network interface and not
        # the standard default route (public network interface).
        self.fixture_log.debug('\n\n**** Add Static Routes **** \n\n')
        addressing_details = ''
        for server_dict in self.servers.itervalues():
            # Add a generalized static route for the general isolated networks
            persona = server_dict[TopologyFixtureRoutines.PERSONA]
            addressing_details += '{0!s}\n'.format(persona)

            interface_to_use = self.get_vm_network_interface_for_ip(
                server_dict=server_dict,
                ip_address=persona.inet_fix_ipv4[0])

            self.add_static_default_route(
                svr_dict=server_dict, network_to_add=network_for_static_route,
                interface=interface_to_use)

        self.fixture_log.debug('\n\n**** SPOKE ADDRESSING DETAILS **** \n\n')
        self.fixture_log.debug(addressing_details)

        return self.servers, self.iso_nets, self.iso_subnets

    def _build_hub_router(self, network_spokes):
        """
        Build the hub router (host) with each spoke's gateway configured as
        a network interface on the router.

        :param network_spokes: [List] List of iso_subnets that define each
            spoke

        :return: VM server model representing the hub router
        """
        port_ids = []
        hub_name = 'HUB_{spokes}_{run_id}'.format(
            spokes=len(network_spokes), run_id=self.RUN_ID)
        hub = {}

        # Iterate across spoke (subnets), and configure each GW IP as an
        # interface on the 'hub' router.
        for spoke in network_spokes:
            network_id = spoke.network_id
            fixed_ips = [{'ip_address': spoke.gateway_ip,
                          'subnet_id': spoke.id}]
            port_resp = self.net.ports.behaviors.create_port(
                network_id=network_id, admin_state_up=True,
                fixed_ips=fixed_ips)

            self.delete_ports.append(port_resp.response.entity.id)
            port_ids.append(port_resp.response.entity.id)

        # Add public and service networks to the hub router
        attached_networks = [self.public_network_id, self.service_network_id]

        hub_svr = self.net.behaviors.create_networking_server(
            name=hub_name, admin_pass=self.ADMIN_PASS,
            network_ids=attached_networks, port_ids=port_ids)
        self.delete_servers.append(hub_svr.entity.id)

        # Store HUB server information
        hub[TopologyFixtureRoutines.SERVER] = hub_svr.entity

        hub_persona = ServerPersona(server=hub_svr.entity)
        hub[TopologyFixtureRoutines.PERSONA] = hub_persona

        proxy = NetworkProxyMgr(use_proxy=False, debug=True)
        proxy.set_proxy_server(hub_svr.entity)
        hub[TopologyFixtureRoutines.PROXY] = proxy

        self.fixture_log.debug("HUB INTERFACE INFO (PARTIAL)\n{0}".format(
            hub_persona))

        # Wait for VM's public network to come online by pinging the server's
        # public interface
        attempt = 0
        max_attempts = 10
        hub_available = False
        while not hub_available and attempt < max_attempts:
            attempt += 1
            self.fixture_log.debug(
                'Verifying hub router is online. Attempt: {0} of {1}'.format(
                    attempt, max_attempts))
            try:
                hub_available = proxy.ping(hub_persona.pnet_fix_ipv4[0])

            except Exception as err:
                self.fixture_log.info('PING EXCEPTION: {0}'.format(err))
                hub_available = False

            if not hub_available:
                time.sleep(5)

        if attempt >= max_attempts:
            self.assertClassSetupFailure(
                'Hub router (hub & spoke topology) never came online. Unable '
                'to proceed.')

        # Give the SSH daemon time to start up. The network is active,
        # but SSH is unstable at this point in the hub's provisioning.
        time.sleep(self.SSH_PROVISION_DELAY)

        # Enable the hub to do basic routing
        self.enable_ip_forwarding(hub)

        return hub
