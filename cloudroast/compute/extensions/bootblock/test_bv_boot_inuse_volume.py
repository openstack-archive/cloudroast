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


class BootInUseVolume(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(BootInUseVolume, cls).setUpClass()
        response = cls.server_behaviors.create_active_server()
        cls.server = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.err_msg = ""

    @tags(type='smoke', net='yes')
    def test_for_inuse_volume_should_not_be_used(self):
        try:
            boot_from_block = {'volume_id': self.server.volume_id,
                               'del_on_termination': None,
                               'device_name': None,
                               'type': None}
            self.response = self.server_behaviors.create_active_server(
                boot_from_block=boot_from_block)
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[35:41], "failed", self.err_msg)
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id, self.servers_client.delete_server)
        self.assertNotEqual(self.err_msg, "",
                            "Server built (should not have been built)")
