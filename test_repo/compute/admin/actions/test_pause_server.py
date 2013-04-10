from cafe.drivers.unittest.decorators import tags
from test_repo.compute.fixtures import ComputeAdminFixture

class PauseServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(PauseServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(PauseServerTests, cls).tearDownClass()

    def test_pause_unpause_server(self):
        self.servers_client.pause_server(self.server.id)
        self.server_behaviors.wait_for_server_status(self.server.id, 'PAUSED')
        self.servers_client.unpause_server(self.server.id)
        self.server_behaviors.wait_for_server_status(self.server.id, 'ACTIVE')