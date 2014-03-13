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

import json

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name

from cloudroast.designate.fixtures import ServersFixture


class ServerTest(ServersFixture):

    @tags('smoke', 'positive')
    def test_list_servers(self):
        self.create_server()
        list_resp = self.server_client.list_servers()
        self.assertEquals(list_resp.status_code, 200)

        servers = list_resp.entity
        self.assertGreater(len(servers), 0)

    @tags('smoke', 'positive')
    def test_create_server(self):
        create_resp = self.create_server()
        self.assertEquals(create_resp.status_code, 200)

        server_id = create_resp.entity.id

        get_resp = self.server_client.get_server(server_id)
        self.assertEquals(get_resp.status_code, 200)

    @tags('smoke', 'positive')
    def test_update_server(self):
        create_resp = self.create_server()
        self.assertEquals(create_resp.status_code, 200)

        server_id = create_resp.entity.id

        new_name = rand_name("new.server") + ".com."
        update_resp = self.server_client.update_server(server_id, new_name)
        self.assertEquals(update_resp.status_code, 200)

    @tags('smoke', 'positive')
    def test_delete_server(self):
        create_resp = self.create_server()
        self.assertEquals(create_resp.status_code, 200)

        server_id = create_resp.entity.id

        del_resp = self.server_client.delete_server(server_id)
        self.assertEquals(del_resp.status_code, 200)

        get_resp = self.server_client.get_server(server_id)
        self.assertEquals(get_resp.status_code, 404)
