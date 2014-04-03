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
from datetime import timedelta

from cloudcafe.common.tools.time import string_to_datetime
from cloudcafe.compute.common.equality_tools import EqualityTools

from cloudroast.stacktach.fixtures import StackTachComputeIntegration,\
    StackTachTestAssertionsFixture


class StackTachDBDeleteServerTests(StackTachComputeIntegration,
                                   StackTachTestAssertionsFixture):
    """
    @summary: With Server Delete, tests the entries created in StackTach DB.
    """
    @classmethod
    def setUpClass(cls):
        cls.create_server()
        cls.delete_server()
        cls.stacktach_events_for_server(server=cls.deleted_server)

    def test_launch_entry_on_create_server_response(self):
        """
        Verify the Launch parameters are being returned in the initial response
        of Server Creation
        """

        self.validate_attributes_in_launch_response()

    def test_launch_entry_fields_on_create_server_response(self):
        """
        Verify that the Launch entry will have all expected fields
        after Server Creation
        """
        self.validate_launch_entry_field_values(server=self.deleted_server)

    def test_delete_entry_on_delete_server_response(self):
        """
        Verify the Delete parameters are being returned from the
        StackTach DB on Server Deletion
        """

        self.assertEqual(len(self.delete_response.entity), 1,
                         self.msg.format("List of Delete objects",
                                         '1',
                                         len(self.delete_response.entity),
                                         self.delete_response.reason,
                                         self.delete_response.content))
        self.assertTrue(self.delete_response.ok,
                        self.msg.format("status_code", 200,
                                        self.delete_response.status_code,
                                        self.delete_response.reason,
                                        self.delete_response.content))
        self.assertTrue(self.event_delete.id_,
                        self.msg.format("id",
                                        "Not None or Empty",
                                        self.event_delete.id_,
                                        self.delete_response.reason,
                                        self.delete_response.content))
        self.assertTrue(self.event_delete.instance,
                        self.msg.format("instance",
                                        "Not None or Empty",
                                        self.event_delete.instance,
                                        self.delete_response.reason,
                                        self.delete_response.content))
        self.assertTrue(self.event_delete.launched_at,
                        self.msg.format("launched_at",
                                        "Not None or Empty",
                                        self.event_delete.launched_at,
                                        self.delete_response.reason,
                                        self.delete_response.content))
        self.assertTrue(self.event_delete.deleted_at,
                        self.msg.format("deleted_at",
                                        "Not None or Empty",
                                        self.event_delete.deleted_at,
                                        self.delete_response.reason,
                                        self.delete_response.content))
        self.assertTrue(self.event_delete.raw,
                        self.msg.format("raw",
                                        "Not None or Empty",
                                        self.event_delete.raw,
                                        self.delete_response.reason,
                                        self.delete_response.content))

    def test_delete_entry_fields_on_delete_server_response(self):
        """
        Verify that the Delete entry will have all expected fields
        after Server Delete
        """

        self.assertEqual(self.deleted_server.id, self.event_delete.instance,
                         self.msg.format("instance",
                                         self.deleted_server.id,
                                         self.event_delete.instance,
                                         self.delete_response.reason,
                                         self.delete_response.content))
        self.assertTrue(
            EqualityTools.are_datetimes_equal(
                string_to_datetime(self.launched_at_created_server),
                string_to_datetime(self.event_delete.launched_at),
                timedelta(seconds=self.leeway)),
            self.msg.format("launched_at",
                            self.launched_at_created_server,
                            self.event_delete.launched_at,
                            self.delete_response.reason,
                            self.delete_response.content))
        self.assertTrue(
            EqualityTools.are_datetimes_equal(
                string_to_datetime(self.deleted_at),
                string_to_datetime(self.event_delete.deleted_at),
                timedelta(seconds=self.leeway)),
            self.msg.format("deleted_at",
                            self.deleted_at,
                            self.event_delete.deleted_at,
                            self.delete_response.reason,
                            self.delete_response.content))

    def test_launched_earlier_than_deleted_on_delete_server_response(self):
        """
        Verify that the Delete entry launched_at is earlier than the
        Delete entry deleted_at for a deleted server
        """

        self.assertLess(
            string_to_datetime(self.event_delete.launched_at),
            string_to_datetime(self.event_delete.deleted_at),
            self.msg.format("launched_at",
                            "launched_at earlier than deleted_at",
                            ' '.join([self.event_delete.launched_at,
                                      self.event_delete.deleted_at]),
                            self.delete_response.reason,
                            self.delete_response.content))

    def test_launched_at_field_match_on_delete_server_response(self):
        """
        Verify that the Delete entry launched_at matches the
        Launch entry launched_at for a deleted server
        """

        self.assertEqual(self.event_delete.launched_at,
                         self.event_launch.launched_at,
                         self.msg.format(
                             "launched_at",
                             self.event_delete.launched_at,
                             self.event_launch.launched_at,
                             self.delete_response.reason,
                             self.delete_response.content))

    def test_instance_field_on_delete_server_response(self):
        """
        Verify that the Delete entry instance matches the
        Launch entry instance for a deleted server
        """

        self.assertEqual(self.event_delete.instance,
                         self.event_launch.instance,
                         self.msg.format("instance",
                                         self.event_delete.instance,
                                         self.event_launch.instance,
                                         self.delete_response.reason,
                                         self.delete_response.content))

    def test_no_exist_entry_on_delete_server_response(self):
        """
        Verify that there is no exist entry on a newly deleted server
        where the deletion occurs before the end of audit period
        """
        self.validate_no_exists_entry_returned()
