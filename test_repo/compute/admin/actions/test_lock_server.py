from cloudcafe.compute.common.exceptions import ActionInProgress, BadRequest
from cloudcafe.compute.common.types import NovaServerRebootTypes
from test_repo.compute.fixtures import ComputeAdminFixture


class LockServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(LockServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.admin_servers_client.lock_server(cls.server.id)

    @classmethod
    def tearDownClass(cls):
        super(LockServerTests, cls).tearDownClass()
        cls.admin_servers_client.unlock_server(cls.server.id)

    def test_cannot_delete_locked_server(self):
        with self.assertRaises(ActionInProgress):
            self.servers_client.delete_server(self.server.id)

    def test_cannot_change_password_of_locked_server(self):
        with self.assertRaises(BadRequest):
            self.servers_client.change_password(self.server.id,
                                                '123abcABC!!')

    def test_cannot_reboot_locked_server(self):
        with self.assertRaises(ActionInProgress):
            self.servers_client.reboot(self.server.id,
                                       NovaServerRebootTypes.SOFT)

    def test_cannot_rebuild_locked_server(self):
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, self.image_ref)

    def test_cannot_resize_locked_server(self):
        with self.assertRaises(ActionInProgress):
            self.servers_client.resize(self.server.id, self.flavor_ref)

