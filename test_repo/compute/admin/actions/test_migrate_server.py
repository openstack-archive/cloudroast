from cloudcafe.compute.common.types import NovaServerStatusTypes
from test_repo.compute.fixtures import ComputeAdminFixture

class MigrateServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(MigrateServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(MigrateServerTests, cls).tearDownClass()

    def test_migrate_server(self):
        self.admin_servers_client.migrate_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.VERIFY_RESIZE)
        self.admin_servers_client.confirm_resize(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE)
