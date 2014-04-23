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


class CreateChassisTest(BareMetalFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateChassisTest, cls).setUpClass()
        cls._create_chassis()

    def test_create_chassis_response_code(self):
        """Verify that the response code for the create chassis
        request is correct.
        """
        self.assertEqual(self.create_chassis_resp.status_code, 201)

    def test_created_chassis_properties(self):
        """Verify that the properties provided to the create chassis request
        are reflected in the created chassis.
        """
        self.assertEqual(self.chassis.description, self.chassis_description)
        self.assertEqual(self.chassis.extra, self.chassis_extra)

    def test_new_chassis_in_list_of_chassis(self):
        """Verify that the newly created chassis exists in the
        list of chassis.
        """
        existing_chassis = self.chassis_client.list_chassis().entity
        chassis_uuids = [chassis.uuid for chassis in existing_chassis]
        self.assertIn(self.chassis.uuid, chassis_uuids)

    def test_new_chassis_in_detailed_list_of_chassis(self):
        """Verify that the newly created chassis exists in the
        detailed list of chassis.
        """
        resp = self.chassis_client.list_chassis_with_details()
        existing_chassis = resp.entity
        chassis_uuids = [chassis.uuid for chassis in existing_chassis]
        self.assertIn(self.chassis.uuid, chassis_uuids)

    def test_get_chassis(self):
        """Verify the details returned by a get chassis request match
        the expected values.
        """
        resp = self.chassis_client.get_chassis(self.chassis.uuid)
        self.assertEqual(resp.status_code, 200)
        chassis = resp.entity
        self.assertEqual(chassis.description, self.chassis_description)
        self.assertEqual(chassis.extra, self.chassis_extra)
