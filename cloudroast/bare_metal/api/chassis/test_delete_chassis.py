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


class DeleteChassisTest(BareMetalFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteChassisTest, cls).setUpClass()
        cls._create_chassis()
        cls.delete_chassis_resp = cls.chassis_client.delete_chassis(
            cls.chassis.uuid)

    def test_delete_chassis_response_code(self):
        """Verify that the response code for the delete chassis
        request is correct.
        """
        self.assertEqual(self.delete_chassis_resp.status_code, 204)

    def test_cannot_get_deleted_chassis(self):
        """Verify that a request fails when the details
        of a deleted chassis are requested.
        """
        resp = self.chassis_client.get_chassis(self.chassis.uuid)
        self.assertEqual(resp.status_code, 404)

    def test_deleted_chassis_not_in_list_of_chassis(self):
        """Verify that a deleted chassis does not exist in the
        list of all chassis.
        """
        existing_chassis = self.chassis_client.list_chassis().entity
        chassis_uuids = [chassis.uuid for chassis in existing_chassis]
        self.assertNotIn(self.chassis.uuid, chassis_uuids)
