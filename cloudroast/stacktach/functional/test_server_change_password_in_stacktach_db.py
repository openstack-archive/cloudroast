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
from cloudroast.stacktach.fixtures import StackTachComputeIntegration,\
    StackTachTestAssertionsFixture


class StackTachDBChangePasswordServerTests(StackTachComputeIntegration,
                                           StackTachTestAssertionsFixture):
    """
    @summary: With Server - Change Password, tests the entries created in
        StackTach DB.
    """
    @classmethod
    def setUpClass(cls):
        cls.create_server()
        cls.change_password_server()
        cls.stacktach_events_for_server(server=cls.changed_password_server)

    def test_launch_entry_on_change_password_server_response(self):
        """
        Verify that the Launch parameters are being returned from the
        StackTach DB after changing the password on the server.
        """
        self.validate_attributes_in_launch_response()

    def test_launch_entry_fields_on_change_password_server_response(self):
        """
        Verify that the Launch entry will have all expected fields from the
        StackTach DB after changing the password on the server.
        """
        self.validate_launch_entry_field_values(
            server=self.changed_password_server)

    def test_no_delete_entry_on_change_password_server_response(self):
        """
        Verify that there is no delete entry on an instance which had
        it's password changed.
        """
        self.validate_no_deletes_entry_returned()

    def test_no_exist_entry_on_change_password_server_response(self):
        """
        Verify that there is no exist entry on an instance which had
        it's password changed.
        """
        self.validate_no_exists_entry_returned()
