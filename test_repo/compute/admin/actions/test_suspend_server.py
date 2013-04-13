from cafe.drivers.unittest.decorators import tags
from test_repo.compute.fixtures import ComputeAdminFixture

class SuspendServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(SuspendServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(SuspendServerTests, cls).tearDownClass()

    def test_suspend_resume_server(self):
        self.admin_servers_client.suspend_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, 'SUSPENDED')
        self.admin_servers_client.resume_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, 'ACTIVE')
