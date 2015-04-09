"""
Copyright 2015 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.exceptions import Forbidden, ItemNotFound, \
    BadRequest
from cloudroast.compute.fixtures import ComputeFixture


class AdminAuthorizationTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates an active server.
        """
        super(AdminAuthorizationTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_lock_server_fails_as_user(self):
        """
        A lock request should fail when not made by an admin.

        Will call lock server expecting a "Forbidden" exception to be raised
        because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.lock_server(self.server.id)

    @tags(type='negative', net='no')
    def test_unlock_server_fails_as_user(self):
        """
        An unlock request should fail when not made by an admin.

        Will call unlock server expecting a "Forbidden" exception to be raised
        because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.unlock_server(self.server.id)

    @tags(type='negative', net='no')
    def test_migrate_server_fails_as_user(self):
        """
        A migrate request should fail when not made by an admin.

        Will call migrate server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.migrate_server(self.server.id)

    @tags(type='negative', net='no')
    def test_live_migrate_server_fails_as_user(self):
        """
        A live migrate request should fail when not made by an admin.

        Will call live migrate server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.live_migrate_server(self.server.id)

    @tags(type='negative', net='no')
    def test_stop_server_fails_as_user(self):
        """
        A stop request should fail when not made by an admin.

        Will call stop server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.stop_server(self.server.id)

    @tags(type='negative', net='no')
    def test_start_server_fails_as_user(self):
        """
        A start request should fail when not made by an admin.

        Will call start server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(BadRequest):
            self.servers_client.start_server(self.server.id)

    @tags(type='negative', net='no')
    def test_suspend_server_fails_as_user(self):
        """
        A suspend request should fail when not made by an admin.

        Will call suspend server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.suspend_server(self.server.id)

    @tags(type='negative', net='no')
    def test_resume_server_fails_as_user(self):
        """
        A resume request should fail when not made by an admin.

        Will call resume server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.resume_server(self.server.id)

    @tags(type='negative', net='no')
    def test_pause_server_fails_as_user(self):
        """
        A pause request should fail when not made by an admin.

        Will call pause server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.pause_server(self.server.id)

    @tags(type='negative', net='no')
    def test_unpause_server_fails_as_user(self):
        """
        An unpause request should fail when not made by an admin.

        Will call unpause server expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.unpause_server(self.server.id)

    @tags(type='negative', net='no')
    def test_reset_server_state_fails_as_user(self):
        """
        A reset server state request should fail when not made by an admin.

        Will call reset server sate expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.reset_state(self.server.id)

    @tags(type='negative', net='no')
    def test_create_flavor_fails_as_user(self):
        """
        A create flavor request should fail when not made by an admin.

        Will call create flavor expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.flavors_client.create_flavor(
                name='test555', ram='128', vcpus='1', disk='10', id='100',
                is_public=True)

    @tags(type='negative', net='no')
    def test_delete_flavor_fails_as_user(self):
        """
        A delete flavor request should fail when not made by an admin.

        Will call delete flavor expecting a "Forbidden" exception to be
        raised because the call is being executed as a non-admin.

        The following assertions occur:
            - Expecting a Forbidden exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.flavors_client.delete_flavor(self.flavor_ref)
