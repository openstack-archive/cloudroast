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

from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudroast.networking.networks.topologies.topology_routines \
    import TopologyFixtureRoutines


class FlatNetworkFixture(
        NetworkingComputeFixture, TopologyFixtureRoutines):

    # NOTE: These should be customized at instantiation, depending on the
    # purpose of the tests associated with the fixture.

    # Number of servers to build as part of the FIXTURE. Tests should build
    # additional VMs if they need to test a specific aspect of the VMs.
    NUM_TO_BUILD = 3

    @classmethod
    def setUpClass(cls):
        super(FlatNetworkFixture, cls).setUpClass()

        # Attributes registered here, populated in setUp()
        cls.iso_net = None
        cls.iso_net_gw = None

        # dictionary key = server_id
        # Sub-dictionary key constants are defined in the
        # TopologyFixtureRoutine class
        # Dictionary Structure:
        #   <server_id>: {PERSONA: <persona_obj>,
        #                 SERVER: <server_model>,
        #                 PROXY: <proxy_model>}
        cls.servers = {}

        # For each network type, this will contain the textual prettytable
        # representation of the results (connectivity between each host)
        # dictionary key = network type (as defined in NetTypes class)
        cls.last_connectivity_check = {}

    def setUp(self):
        super(FlatNetworkFixture, self).setUp()

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
            '(Number of servers: {num})'.format(num=self.NUM_TO_BUILD))

        num_to_build = 0
        if len(self.servers.keys()) < self.NUM_TO_BUILD:
            num_to_build = self.NUM_TO_BUILD - len(self.servers.keys())

        for num in xrange(num_to_build):
            svr_num = num + len(self.servers.keys())
            self.fixture_log.debug('Building server number: {0} of {1}'.format(
                svr_num + 1, num_to_build))
            self._build_and_register_iso_net_server(
                svr_id_num=svr_num, iso_network=self.iso_network)

        # Verify initial connectivity
        connectivity = self.verify_ping_connectivity(
            ping_count=self.DEFAULT_PING_COUNT)

        if self.DEBUG and not connectivity:
            self.debug_topology_routine()
        else:
            self.assertTrue(connectivity, self.connectivity_error())
