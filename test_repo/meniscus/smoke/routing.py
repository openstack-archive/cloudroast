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

from test_repo.meniscus.fixtures import PairingFixture


class TestRouting(PairingFixture):

    def test_get_worker_routing(self):
        response = self.pairing_behaviors.pair_worker_from_config()
        pairing_info = response.entity
        self.assertIsNotNone(pairing_info)

        response = self.pairing_client.get_routing(
            worker_id=pairing_info.worker_id,
            worker_token=pairing_info.worker_token)

        self.assertEqual(200, response.status_code)
