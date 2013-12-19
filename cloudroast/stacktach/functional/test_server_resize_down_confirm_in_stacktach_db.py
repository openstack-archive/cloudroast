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
from datetime import datetime

from cloudcafe.compute.common.constants import Constants
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudroast.stacktach.fixtures import ConfirmResizeServerFixture,\
    StackTachTestAssertionsFixture


class StackTachDBServerResizeDownConfirmTests(ConfirmResizeServerFixture,
                                              StackTachTestAssertionsFixture):
    """
    @summary: With Server Resize Down (e.g., from flavor 3 -> 2),
      tests the entries created in StackTach DB.
    """

    @classmethod
    def setUpClass(cls):
        cls.flavors_config = FlavorsConfig()
        cls.flavor_ref = cls.flavors_config.primary_flavor
        cls.flavor_ref_alt = cls.flavors_config.secondary_flavor
        if cls.flavor_ref > cls.flavor_ref_alt:
            raise cls.assertClassSetupFailure(
                'flavor_ref should not be greater than flavor_ref_alt. '
                'flavor_ref: {0}  flavor_ref_alt: {1}'.format(
                    cls.flavor_ref, cls.flavor_ref_alt))

        super(StackTachDBServerResizeDownConfirmTests, cls).setUpClass(
            flavor_ref=cls.flavor_ref_alt,
            resize_flavor=cls.flavor_ref)
        cls.audit_period_beginning = \
            datetime.utcnow().strftime(Constants.DATETIME_0AM_FORMAT)

        cls.stacktach_events_for_server(server=cls.confirmed_resized_server)
        cls.event_launch_resize_server = cls.event_launches[1]

    def test_launch_entry_on_resize_server_down_response(self):
        """
        Verify the Launch parameters are being returned in the
        Server Resize Down response
        """
        # There should be 2 launch entries for a resize.
        self.validate_attributes_in_launch_response(num_of_launch_entry=2)

    def test_launch_entry_fields_on_create_server(self):
        """
        Verify that the first Launch entry will have all expected fields
        after a Server Resize Down
        """
        self.validate_launch_entry_field_values(
            server=self.created_server,
            expected_flavor_ref=self.flavor_ref_alt)

    def test_launch_entry_fields_on_resize_down(self):
        """
        Verify that the second Launch entry will have all expected fields
        after a Server Resize Down
        """
        self.validate_launch_entry_field_values(
            server=self.verify_resized_server,
            event_launch_server=self.event_launch_resize_server)

    def test_exist_entry_on_resize_down_server_response(self):
        """
        Verify the Exist parameters are correct after a Server Resize Down
        """
        self.validate_attributes_in_exist_response()

    def test_exists_entry_fields_on_resize_down(self):
        """
        Verify that the Exist entry will have all expected fields
        after Server Resize Down
        """
        self.validate_exist_entry_field_values(
            server=self.created_server,
            expected_flavor_ref=self.flavor_ref_alt)

    def test_exist_launched_at_field_match_on_resize_down(self):
        """
        Verify that the Exists entry launched_at matches the
        Launch entry launched_at for a Server Resize down
        """

        self.assertEqual(self.event_launch.launched_at,
                         self.event_exist.launched_at,
                         self.msg.format(
                             "launched_at",
                             self.event_launch.launched_at,
                             self.event_exist.launched_at,
                             self.exist_response.reason,
                             self.exist_response.content))

    def test_no_delete_entry_on_resize_down_server_response(self):
        """
        Verify that there is no delete entry after a Server Resize Down
        """
        self.validate_no_deletes_entry_returned()
