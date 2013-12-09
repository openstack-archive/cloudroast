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
from cloudroast.stacktach.fixtures import StackTachCreateServerFixture


class StackTachDBCreateServerTests(StackTachCreateServerFixture):
    """
    @summary: With Server Create, test the entries created in StackTach DB.
    """
    @classmethod
    def setUpClass(cls):
        super(StackTachDBCreateServerTests, cls).setUpClass()

    def test_launch_entry_on_create_server_response(self):
        """
        Verify the Launch parameters are being returned in the initial response
        of Server Creation
        """

        self.assertEqual(len(self.st_launch_response.entity), 1,
                         self.msg.format("List of Launch objects", '1',
                                         len(self.st_launch_response.entity),
                                         self.st_launch_response.reason,
                                         self.st_launch_response.content))
        self.assertTrue(self.st_launch_response.ok,
                        self.msg.format("status_code", 200,
                                        self.st_launch_response.status_code,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.id_,
                        self.msg.format("id",
                                        "Not None or Empty",
                                        self.st_launch_create_server.id_,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.request_id,
                        self.msg.format(
                            "request_id",
                            "Not None or Empty",
                            self.st_launch_create_server.request_id,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.instance,
                        self.msg.format("instance",
                                        "Not None or Empty",
                                        self.st_launch_create_server.instance,
                                        self.st_launch_response.reason,
                                        self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.launched_at,
                        self.msg.format(
                            "launched_at",
                            "Not None or Empty",
                            self.st_launch_create_server.launched_at,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.instance_type_id,
                        self.msg.format(
                            "instance_type_id",
                            "Not None or Empty",
                            self.st_launch_create_server.instance_type_id,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.instance_flavor_id,
                        self.msg.format(
                            "instance_flavor_id",
                            "Not None or Empty",
                            self.st_launch_create_server.instance_flavor_id,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.tenant,
                        self.msg.format(
                            "tenant",
                            "Not None or Empty",
                            self.st_launch_create_server.tenant,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.os_distro,
                        self.msg.format(
                            "os_distro",
                            "Not None or Empty",
                            self.st_launch_create_server.os_distro,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.os_version,
                        self.msg.format(
                            "os_version",
                            "Not None or Empty",
                            self.st_launch_create_server.os_version,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.os_architecture,
                        self.msg.format(
                            "os_architecture",
                            "Not None or Empty",
                            self.st_launch_create_server.os_architecture,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))
        self.assertTrue(self.st_launch_create_server.rax_options,
                        self.msg.format(
                            "rax_options",
                            "Not None or Empty",
                            self.st_launch_create_server.rax_options,
                            self.st_launch_response.reason,
                            self.st_launch_response.content))

    def test_launch_entry_fields_on_create_server_response(self):
        """
        Verify that the Launch entry will have all expected fields
        after Server Creation
        """

        self.assertEqual(self.created_server.id,
                         self.st_launch_create_server.instance,
                         self.msg.format(
                             "instance",
                             self.created_server.id,
                             self.st_launch_create_server.instance,
                             self.st_launch_response.reason,
                             self.st_launch_response.content))
        self.assertEqual(self.created_server.flavor.id,
                         self.st_launch_create_server.instance_type_id,
                         self.msg.format(
                             "instance_type_id",
                             self.created_server.flavor.id,
                             self.st_launch_create_server.instance_type_id,
                             self.st_launch_response.reason,
                             self.st_launch_response.content))
        self.assertEqual(self.flavor_ref,
                         self.st_launch_create_server.instance_type_id,
                         self.msg.format(
                             "instance_type_id",
                             self.flavor_ref,
                             self.st_launch_create_server.instance_type_id,
                             self.st_launch_response.reason,
                             self.st_launch_response.content))
        self.assertEqual(self.flavor_ref,
                         self.st_launch_create_server.instance_flavor_id,
                         self.msg.format(
                             "instance_flavor_id",
                             self.flavor_ref,
                             self.st_launch_create_server.instance_flavor_id,
                             self.st_launch_response.reason,
                             self.st_launch_response.content))

    def test_no_delete_entry_on_create_server_response(self):
        """Verify that there is no delete entry on a newly created server"""

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

    def test_no_exist_entry_on_create_server_response(self):
        """Verify that there is no exist entry on a newly created server"""

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
