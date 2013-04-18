"""
Copyright 2013 Rackspace

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
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudcafe.compute.common.types import NovaServerStatusTypes
from test_repo.compute.fixtures import ComputeFixture


class ServersTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServersTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resp = cls.servers_client.delete_server(cls.server.id)
        cls.server_behaviors.wait_for_server_status(cls.server.id,
                                                    NovaServerStatusTypes.DELETED)

    def test_delete_server_response(self):
        self.assertEqual(204, self.resp.status_code)

    def test_get_deleted_server_fails(self):
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(self.server.id)

