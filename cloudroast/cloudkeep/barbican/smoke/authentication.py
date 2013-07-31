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

import unittest2

from cafe.drivers.unittest.decorators import tags
from cloudroast.cloudkeep.barbican.fixtures import AuthenticationFixture


class AuthenticationAPI(AuthenticationFixture):

    @unittest2.skip('Not testing until after M2')
    @tags(type='positive')
    def test_get_version_w_authentication(self):
        """Covers acquiring an authentication token and using it to get the
        version. Only getting the version is implemented with authentication.
        """
        access = self.auth_behaviors.get_access_data(
            self.keystone.username,
            self.keystone.password,
            self.keystone.tenant_name)
        token = access.token.id_

        headers = {'X-Auth-Token': token,
                   'Accept': 'applicaton/json'}
        resp = self.version_client.get_version(headers=headers)

        version = resp.entity

        self.assertEqual(resp.status_code, 200,
                         'Returned unexpected response code')
        self.assertEqual(version.v1, 'current')
        self.assertIsNotNone(version.build)
        self.assertGreater(len(version.build), 0)
