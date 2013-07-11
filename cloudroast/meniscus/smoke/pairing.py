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
from uuid import UUID
from cloudroast.meniscus.fixtures import PairingFixture


class TestPairing(PairingFixture):

    def test_pairing(self):
        response = self.pairing_behaviors.pair_worker_from_config()
        pairing_info = response.entity

        self.assertIsNotNone(pairing_info)
        self.assertIn(self.pairing_config.personality,
                      pairing_info.personality_module)

        # Checking to see if the returned uid is valid
        try:
            UUID(response.entity.worker_token)
            UUID(response.entity.worker_id)
        except ValueError as err:
            self.fail("Invalid uid received from pairing call: {}".format(err))
