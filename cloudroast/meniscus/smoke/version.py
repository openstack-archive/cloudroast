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

from cloudroast.meniscus.fixtures import VersionFixture


class TestVersion(VersionFixture):

    def test_get_version(self):
        response = self.client.get_version()
        version_list = response.entity

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(version_list), 0, "version list is empty")
        self.assertEqual(version_list[0].v1, 'current')
