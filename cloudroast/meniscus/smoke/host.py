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
from cloudroast.meniscus.fixtures import HostFixture


class TestHost(HostFixture):

    def test_create_host(self):
        result = self.host_behaviors.create_new_host(
            ip_v4=self.tenant_config.ip_address_v4,
            ip_v6=self.tenant_config.ip_address_v6,
            profile_id=self.profile_id)
        self.assertEqual(result['request'].status_code, 201)

    def test_delete_host(self):
        result = self.host_behaviors.create_new_host()
        response = self.host_behaviors.delete_host(result['host_id'])

        self.assertEqual(response.status_code, 200)

    def test_update_host(self):
        host_result = self.host_behaviors.create_new_host()

        # We currently have to set all values on the update due to an issue
        # when profile_id is equal to None.
        host_id = host_result['host_id']
        self.host_client.update_host(host_id=host_id,
                                     hostname='new_hostname',
                                     ip_v4='10.10.1.2',
                                     ip_v6='::1',
                                     profile_id=self.profile_id)

        host_response = self.host_client.get_host(host_id)
        host = host_response.entity

        self.assertEqual(host_response.status_code, 200,
                         'Status code should have been 200 OK')
        self.assertEqual(host.hostname, 'new_hostname', 'Incorrect hostname')
        self.assertEqual(host.ip_address_v4, '10.10.1.2')
        self.assertEqual(host.ip_address_v6, '::1')

    def test_get_host(self):
        host_result = self.host_behaviors.create_new_host()
        host_id = host_result['host_id']

        host_response = self.host_client.get_host(host_id)
        host = host_response.entity

        self.assertEqual(200, host_response.status_code,
                         'Status code should have been 200 OK')
        self.assertIsNotNone(host)
        self.assertEqual('testhost', host.hostname, 'Incorrect hostname')
        self.assertEqual(host_id, host.id, 'Unexpected host id')

    def test_get_all_hosts(self):
        first_hostname = self.tenant_config.hostname
        second_hostname = 'testhost_2'

        host1_result = self.host_behaviors.create_new_host(first_hostname)
        host2_result = self.host_behaviors.create_new_host(second_hostname)

        host1 = self.host_client.get_host(host1_result['host_id']).entity
        host2 = self.host_client.get_host(host2_result['host_id']).entity

        hosts_resp = self.host_client.get_all_hosts()
        hosts = hosts_resp.entity

        self.assertEqual(200, hosts_resp.status_code)
        self.assertEqual(len(hosts), 2)
        self.assertIn(host1, hosts)
        self.assertIn(host2, hosts)
