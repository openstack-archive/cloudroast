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
from cloudroast.cloudkeep.barbican.fixtures import VersionFixture


class TestVersion(VersionFixture):

    @tags(type='positive')
    def test_get_version(self):
        """Covers getting the version of Barbican."""
        response = self.client.get_version()
        version = response.entity

        self.assertEqual(response.status_code, 200)
        self.assertEqual(version.v1, 'current')
        self.assertIsNotNone(version.build)
        self.assertGreater(len(version.build), 0)
