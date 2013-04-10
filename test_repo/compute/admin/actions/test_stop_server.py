from cafe.drivers.unittest.decorators import tags
from test_repo.compute.fixtures import ComputeAdminFixture

class StopServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(StopServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(StopServerTests, cls).tearDownClass()

    def test_stop_start_server(self):
        self.servers_client.stop_server(self.server.id)
        self.server_behaviors.wait_for_server_status(self.server.id, 'SHUTOFF')
        self.servers_client.start_server(self.server.id)
        self.server_behaviors.wait_for_server_status(self.server.id, 'ACTIVE')