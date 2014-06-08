"""
Copyright 2014 Rackspace

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

from cloudroast.bare_metal.fixtures import BareMetalFixture


class ListDriversTest(BareMetalFixture):

    def test_list_drivers(self):
        """Verify that the driver is returned in the list of drivers."""
        resp = self.drivers_client.list_drivers()
        self.assertEqual(resp.status_code, 200)

        drivers = resp.entity
        driver_names = [driver.name for driver in drivers]
        self.assertIn('fake', driver_names)
