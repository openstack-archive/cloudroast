from cafe.drivers.unittest.decorators import tags
from test_repo.compute.fixtures import ComputeAdminFixture

class ResetServerStateTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(ResetServerStateTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(ResetServerStateTests, cls).tearDownClass()

    def test_set_server_state(self):

        # Set the active server into error status
        self.servers_client.reset_state(self.server.id, 'error')
        current_server = self.servers_client.get_server(self.server.id).entity
        self.assertEqual(current_server.status.lower(), 'error')

        # Reset the server's error status back to active
        self.servers_client.reset_state(self.server.id, 'active')
        current_server = self.servers_client.get_server(self.server.id).entity
        self.assertEqual(current_server.status.lower(), 'active')