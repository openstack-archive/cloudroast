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
from cloudroast.compute.fixtures import ComputeFixture


class LimitsTest(ComputeFixture):

    @tags(type='smoke', net='no')
    def test_list_limits(self):
        """
        This will call the get limits and sure a successful call

        Will call get_limits from cloudcafe's limits_client
        The following assertions occur
            - 200 status code from the http call
        """
        response = self.limits_client.get_limits()
        self.assertEqual(response.status_code, 200)
