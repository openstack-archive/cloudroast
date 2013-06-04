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
from test_repo.meniscus.fixtures import StatusFixture


class TestStatus(StatusFixture):

    def setUp(self):
        super(TestStatus, self).setUp()
        self.pairing_resp = self.pairing_behaviors.pair_worker_from_config()
        self.assertEqual(self.pairing_resp.status_code, 202)
        self.pairing_info = self.pairing_resp.entity

    def get_worker_entity(self):
        worker_id = self.pairing_info.worker_id
        resp = self.status_client.get_worker_status(worker_id)

        self.assertEqual(resp.status_code, 200)
        return resp.entity

    def test_update_worker_status(self):
        response = self.pairing_client.update_status(
            worker_id=self.pairing_info.worker_id,
            worker_token=self.pairing_info.worker_token,
            status='online')

        self.assertEqual(200, response.status_code)

    def test_update_worker_load_average(self):
        resp = self.status_client.update_load(
            worker_id=self.pairing_info.worker_id,
            worker_token=self.pairing_info.worker_token,
            one=0.1,
            five=0.2,
            fifteen=0.3)

        #TODO: We are still uncertain if this is suppose to be 200
        self.assertEqual(resp.status_code, 200)

        #TODO: Add verification asserts

    def test_update_worker_disk_usage(self):
        total, used = 100000, 30000
        disk = {'/dev/sda1/': {'total': total, 'used': used}}

        resp = self.status_client.update_usage(
            worker_id=self.pairing_info.worker_id,
            worker_token=self.pairing_info.worker_token,
            disks=disk)

        #TODO: We are still uncertain if this is suppose to be 200
        self.assertEqual(resp.status_code, 200)

        worker = self.get_worker_entity()
        partition = worker.system_info.disk_usage.partitions[0]
        self.assertEqual(partition.total, total)
        self.assertEqual(partition.used, used)

    def test_get_worker_status(self):
        worker = self.get_worker_entity()
        self.assertEqual(worker.hostname, self.pairing_config.hostname)

    def test_get_worker_statuses(self):
        resp = self.status_client.get_all_worker_statuses()
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.entity.workers, 0)
