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
        self.admin_servers_client.stop_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, 'SHUTOFF')
        self.admin_servers_client.start_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, 'ACTIVE')
