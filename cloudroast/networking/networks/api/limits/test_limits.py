"""
Copyright 2015 Rackspace

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
from cafe.drivers.unittest.fixtures import BaseTestFixture

from cloudcafe.networking.networks.extensions.limits_api.composites \
    import LimitsComposite


class LimitsGetTest(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super(LimitsGetTest, cls).setUpClass()
        cls.limits = LimitsComposite()

    @tags('smoke')
    def test_get_user_limits(self):
        """
        @summary: Get user rate limits test
        """
        resp = self.limits.behaviors.get_limits()

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
