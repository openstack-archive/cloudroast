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

    @tags(type='positive')
    def test_get_version_w_authentication(self):
        """Covers acquiring an authentication token and using it to get the
        version. Only getting the version is implemented with authentication.
        """
        token, tenant_id = self._get_token_and_id(
            endpoint=self.keystone.authentication_endpoint,
            username=self.keystone.username,
            password=self.keystone.password,
            tenant=self.keystone.tenant_name,
            auth_type=self.keystone.auth_type)

        headers = {'X-Auth-Token': token,
                   'Accept': 'application/json'}
        resp = self.version_client.get_version(headers=headers)

        version = resp.entity

        self.assertEqual(resp.status_code, 200,
                         'Returned unexpected response code')
        self.assertEqual(version.v1, 'current')
        self.assertIsNotNone(version.build)
        self.assertGreater(len(version.build), 0)
