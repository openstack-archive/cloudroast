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
from cloudroast.meniscus.fixtures import StatusFixture


class TestStatus(StatusFixture):

    def test_get_worker_statuses(self):
        resp = self.status_client.get_all_worker_statuses()
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.entity.workers, 0)
