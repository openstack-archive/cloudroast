from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class DevelopmentTesting(NetworkingComputeFixture):

    @tags('development')
    def test_new_stuff(self):
        """
        @summary: for testing new things
        """
        print 'hola mundo'
        print self.config.keep_servers
