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
from datetime import timedelta, datetime

from cloudcafe.common.tools.time import string_to_datetime
from cloudcafe.compute.common.constants import Constants
from cloudcafe.compute.common.equality_tools import EqualityTools
from cloudroast.stacktach.fixtures import StackTachComputeIntegration,\
    StackTachTestAssertionsFixture


class StackTachDBRebuildServerTests(StackTachComputeIntegration,
                                    StackTachTestAssertionsFixture):
    """
    @summary: With Server Rebuild, tests the entries created in StackTach DB.
    """

    @classmethod
    def setUpClass(cls):
        cls.create_server()
        cls.rebuild_server()
        cls.audit_period_beginning = \
            datetime.utcnow().strftime(Constants.DATETIME_0AM_FORMAT)

        cls.stacktach_events_for_server(cls.rebuilt_server)
        cls.event_launch_rebuilt_server = cls.event_launches[1]

    def test_launch_entry_on_rebuild_server_response(self):
        """
        Verify the Launch parameters are being returned in the
        Server Rebuild response
        """
        self.validate_attributes_in_launch_response(num_of_launch_entry=2)

    def test_launch_entry_fields_on_create_server(self):
        """
        Verify that the first Launch entry will have all expected fields
        after a Server Rebuild
        """
        self.validate_launch_entry_field_values(server=self.rebuilt_server)

    def test_launch_entry_fields_on_rebuild(self):
        """
        Verify that the second Launch entry will have all expected fields
        after a Server Rebuild
        """
        self.validate_launch_entry_field_values(
            server=self.rebuilt_server,
            event_launch_server=self.event_launch_rebuilt_server,
            launched_at=self.launched_at_rebuilt_server)

    def test_exist_entry_on_rebuild(self):
        """
        Verify the Exist parameters are correct after a Server Rebuild
        """
        self.validate_attributes_in_exist_response()

    def test_exists_entry_fields_on_rebuild_server_response(self):
        """
        Verify that the Exist entry will have all expected fields
        after Server Rebuild
        """
        self.validate_exist_entry_field_values(server=self.rebuilt_server)
        self.assertTrue(EqualityTools.are_datetimes_equal(
            string_to_datetime(self.rebuild_start_time),
            string_to_datetime(self.event_exist.audit_period_ending),
            timedelta(seconds=self.leeway)))
        self.assertTrue(EqualityTools.are_datetimes_equal(
            string_to_datetime(self.audit_period_beginning),
            string_to_datetime(self.event_exist.audit_period_beginning),
            timedelta(seconds=self.leeway)))
        self.assertTrue(EqualityTools.are_datetimes_equal(
            string_to_datetime(self.rebuild_start_time),
            string_to_datetime(self.event_exist.received),
            timedelta(seconds=self.leeway)))

    def test_exist_launched_at_field_match_on_rebuild(self):
        """
        Verify that the Exists entry launched_at matches the
        Launch entry launched_at for a Server Rebuild
        """
        self.assertEqual(self.event_launch.launched_at,
                         self.event_exist.launched_at,
                         self.msg.format(
                             "launched_at",
                             self.event_launch.launched_at,
                             self.event_exist.launched_at,
                             self.exist_response.reason,
                             self.exist_response.content))

    def test_no_delete_entry_on_rebuild_server_response(self):
        """Verify that there is no delete entry after a Server Rebuild"""
        self.validate_no_deletes_entry_returned()
