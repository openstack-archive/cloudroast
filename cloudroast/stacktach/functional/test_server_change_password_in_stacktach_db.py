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
from cloudroast.stacktach.fixtures import StackTachChangePasswordServerFixture\
    as STChangePasswordServerFixture


class StackTachDBChangePasswordServerTests(STChangePasswordServerFixture):
    """
    @summary: With Server - Change Password, tests the entries created in
        StackTach DB.
    """
    @classmethod
    def setUpClass(cls):
        super(StackTachDBChangePasswordServerTests, cls).setUpClass()

    def test_launch_entry_on_change_password_server_response(self):
        """
        Verify that the Launch parameters are being returned from the
        StackTach DB after changing the password on the server.
        """

        self.assertEqual(len(self.st_launch_response.entity), 1,
                         self.msg.format("List of Launch objects",
                                         '1',
                                         len(self.st_launch_response.entity),
                                         self.st_launch_response.reason,
                                         self.st_launch_response.content))
        self.assertTrue(self.st_launch_response.ok,
                        self.msg.format("status_code", 200,
                                        self.st_launch_response.status_code,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.id_,
                        self.msg.format("id",
                                        "Not None or Empty",
                                        self.st_launch.id_,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.request_id,
                        self.msg.format("request_id",
                                        "Not None or Empty",
                                        self.st_launch.request_id,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.instance,
                        self.msg.format("instance",
                                        "Not None or Empty",
                                        self.st_launch.instance,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.launched_at,
                        self.msg.format("launched_at",
                                        "Not None or Empty",
                                        self.st_launch.launched_at,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.instance_type_id,
                        self.msg.format("instance_type_id",
                                        "Not None or Empty",
                                        self.st_launch.instance_type_id,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.instance_flavor_id,
                        self.msg.format("instance_flavor_id",
                                        "Not None or Empty",
                                        self.st_launch.instance_flavor_id,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.tenant,
                        self.msg.format("tenant",
                                        "Not None or Empty",
                                        self.st_launch.tenant,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.os_distro,
                        self.msg.format("os_distro",
                                        "Not None or Empty",
                                        self.st_launch.os_distro,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.os_version,
                        self.msg.format("os_version",
                                        "Not None or Empty",
                                        self.st_launch.os_version,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.os_architecture,
                        self.msg.format("os_architecture",
                                        "Not None or Empty",
                                        self.st_launch.os_architecture,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch.rax_options,
                        self.msg.format("rax_options",
                                        "Not None or Empty",
                                        self.st_launch.rax_options,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))

    def test_launch_entry_fields_on_change_password_server_response(self):
        """
        Verify that the Launch entry will have all expected fields from the
        StackTach DB after changing the password on the server.
        """

        self.assertEqual(self.created_server.id, self.st_launch.instance,
                         self.msg.format("instance",
                                         self.created_server.id,
                                         self.st_launch.instance,
                                         self.st_launch_response.reason,
                                         self.st_launch_response.content))
        self.assertEqual(self.created_server.flavor.id,
                         self.st_launch.instance_type_id,
                         self.msg.format("instance_type_id",
                                         self.created_server.flavor.id,
                                         self.st_launch.instance_type_id,
                                         self.st_launch_response.reason,
                                         self.st_launch_response.content))
        self.assertEqual(self.flavor_ref,
                         self.st_launch.instance_type_id,
                         self.msg.format("instance_type_id",
                                         self.flavor_ref,
                                         self.st_launch.instance_type_id,
                                         self.st_launch_response.reason,
                                         self.st_launch_response.content))
        self.assertEqual(self.flavor_ref,
                         self.st_launch.instance_flavor_id,
                         self.msg.format("instance_flavor_id",
                                         self.flavor_ref,
                                         self.st_launch.instance_flavor_id,
                                         self.st_launch_response.reason,
                                         self.st_launch_response.content))

    def test_no_delete_entry_on_change_password_server_response(self):
        """
        Verify that there is no delete entry on an instance which had
        it's password changed.
        """

        self.assertTrue(self.st_delete_response.ok,
                        self.msg.format("status_code",
                                        200,
                                        self.st_delete_response.status_code,
                                        self.st_delete_response.reason,
                                        self.st_delete_response.content))
        self.assertFalse(self.st_delete,
                         self.msg.format("Non-empty List of Delete objects",
                                         "Empty List", self.st_delete,
                                         self.st_delete_response.reason,
                                         self.st_delete_response.content))

    def test_no_exist_entry_on_change_password_server_response(self):
        """
        Verify that there is no exist entry on an instance which had
        it's password changed.
        """

        self.assertTrue(self.st_exist_response.ok,
                        self.msg.format("status_code",
                                        200,
                                        self.st_exist_response.status_code,
                                        self.st_exist_response.reason,
                                        self.st_exist_response.content))
        self.assertFalse(self.st_exist,
                         self.msg.format("Non-empty List of Exist objects",
                                         "Empty List", self.st_exist,
                                         self.st_exist_response.reason,
                                         self.st_exist_response.content))
