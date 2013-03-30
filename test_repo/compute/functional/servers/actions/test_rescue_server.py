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
from test_repo.compute.fixtures import ComputeFixture


class ServerRescueTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerRescueTests, cls).setUpClass()
        server_response = cls.compute_provider.create_active_server()
        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        flavor_response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = flavor_response.entity

    @classmethod
    def tearDownClass(cls):
        super(ServerRescueTests, cls).tearDownClass()

    @tags(type='smoke', net='yes')
    def test_rescue_and_unrescue_server_test(self):
        """Verify that a server can enter and exit rescue mode"""
        rescue_response = self.servers_client.rescue(self.server.id)
        changed_password = rescue_response.entity.adminPass
        self.assertTrue(rescue_response.status_code is 200,
                        msg="The response code while rescuing a server is %s instead of 200" % rescue_response.status_code)
        self.assertTrue(self.server.adminPass is not changed_password,
                        msg="The password did not change after Rescue.")

        #Enter rescue mode
        rescue_server_response = self.compute_provider.wait_for_server_status(self.server.id, 'RESCUE')
        rescue_server = rescue_server_response.entity
        rescue_server.adminPass = changed_password

        remote_client = self.compute_provider.get_remote_instance_client(rescue_server)

        #Verify if hard drives are attached
        remote_client = self.compute_provider.get_remote_instance_client(rescue_server)
        partitions = remote_client.get_partition_details()
        self.assertEqual(3, len(partitions))

        #Exit rescue mode
        unrescue_response = self.servers_client.unrescue(self.server.id)
        self.assertTrue(unrescue_response.status_code == 202,
                        msg="The response code while unrescuing a server is %s instead of 202" % rescue_response.status_code)

        self.compute_provider.wait_for_server_status(self.server.id, 'ACTIVE')
        remote_client = self.compute_provider.get_remote_instance_client(self.server)
        partitions = remote_client.get_partition_details()
        self.assertEqual(2, len(partitions), msg="The number of partitions after unrescue were not two.")
        result, message = remote_client.verify_partitions(self.flavor.disk, self.flavor.swap, 'active', partitions)
        self.assertTrue(result, msg=message)
