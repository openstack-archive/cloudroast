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
from cloudroast.compute.fixtures import ComputeFixture


class DeleteServerBurnIn(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteServerBurnIn, cls).setUpClass()
        resp = cls.server_behaviors.create_active_server()
        cls.server = resp.entity

    @tags(type='burn-in', net='no')
    def test_delete_server(self):
        self.servers_client.delete_server(self.server.id)
        self.server_behaviors.wait_for_server_to_be_deleted(self.server.id)
