from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.exceptions import BadRequest
from test_repo.compute.fixtures import ComputeFixture


class AdminAuthorizationTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(AdminAuthorizationTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(AdminAuthorizationTest, cls).tearDownClass()

    def test_lock_server_fails_as_user(self):
        """A lock request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.lock_server(self.server.id)

    def test_unlock_server_fails_as_user(self):
        """An unlock request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.unlock_server(self.server.id)

    def test_migrate_server_fails_as_user(self):
        """A migrate request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.migrate_server(self.server.id)

    def test_live_migrate_server_fails_as_user(self):
        """A live migrate request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.live_migrate_server(self.server.id)

    def test_stop_server_fails_as_user(self):
        """A stop request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.stop_server(self.server.id)

    def test_start_server_fails_as_user(self):
        """A start request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.start_server(self.server.id)

    def test_suspend_server_fails_as_user(self):
        """A suspend request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.suspend_server(self.server.id)

    def test_resume_server_fails_as_user(self):
        """A resume request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.resume_server(self.server.id)

    def test_pause_server_fails_as_user(self):
        """A pause request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.pause_server(self.server.id)

    def test_unpause_server_fails_as_user(self):
        """An unpause request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.unpause_server(self.server.id)

    def test_reset_server_state_fails_as_user(self):
        """A reset state request should fail when not made by an admin"""
        with self.assertRaises(BadRequest):
            self.servers_client.reset_state(self.server.id)
