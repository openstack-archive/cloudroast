import time

from cafe.drivers.unittest.decorators import tags
from cloudroast.networking.networks.topologies.spoke_and_hub_fixture \
    import SpokeAndHubFixture


class TestSpokeAndHubTopology(SpokeAndHubFixture):
    NUM_OF_SPOKES = 3
    DEBUG = False

    @tags('spoke_and_hub', 'topology', 'connectivity')
    def test_basic_spoke_and_hub_connectivity(self):
        """ Basic topology connectivity verification. """

        # The validation of the topology is actually done as part of the
        # topology setup, but this will allow a basic connectivity test in
        # the setup to occur. If there is an issue with connectivity, the setup
        # will error report the issues.
        pass

    def debug_topology_routine(self):
        """
        For debugging only. If the class DEBUG flag is set, and connectivity
        fails, this routine will be invoked by the setup routine.

        """
        delay_minutes = 15
        print("Connectivity Issues detected!\n You have {delay} minutes to "
               "debug. GO!".format(delay=delay_minutes))
        time.sleep(delay_minutes * 60)
