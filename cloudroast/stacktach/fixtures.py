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
from datetime import datetime, timedelta

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.common.tools.time import string_to_datetime
from cloudcafe.compute.common.constants import Constants
from cloudcafe.compute.common.equality_tools import EqualityTools
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates, NovaServerRebootTypes as RebootTypes
from cloudcafe.compute.servers_api.config import ServersConfig
from cloudcafe.stacktach.v2.config import StacktachConfig, MarshallingConfig
from cloudcafe.stacktach.v2.stacktach_db_api.behaviors import StackTachDBBehavior
from cloudcafe.stacktach.v2.stacktach_db_api.client import StackTachDBClient
from cloudcafe.stacktach.v2.stacky_api.behaviors import StackTachBehavior
from cloudcafe.stacktach.v2.stacky_api.client import StackTachClient
from cloudroast.compute.fixtures import ComputeFixture


class StackTachFixture(BaseTestFixture):
    """
    @summary: Fixture for any StackTach test.
    """
    @classmethod
    def setUpClass(cls):
        super(StackTachFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.stacktach_config = StacktachConfig()
        cls.days_passed = cls.stacktach_config.days_passed
        cls.msg = "Unexpected {0} value received. Expected: {1}," \
                  "Received: {2}, Reason: {3}, Contents: {4}"

        cls.url = cls.stacktach_config.url
        cls.serializer = cls.marshalling.serializer
        cls.deserializer = cls.marshalling.deserializer

        cls.stacktach_client = StackTachClient(cls.url, cls.serializer,
                                               cls.deserializer)
        cls.stacktach_behavior = StackTachBehavior(cls.stacktach_client,
                                                   cls.stacktach_config)


class StackTachDBFixture(BaseTestFixture):
    """
    @summary: Fixture for any StackTachDB test.
    """
    @classmethod
    def setUpClass(cls):
        super(StackTachDBFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.servers_config = ServersConfig()
        cls.leeway = cls.servers_config.server_build_timeout
        cls.stacktach_config = StacktachConfig()
        cls.days_passed = cls.stacktach_config.days_passed
        cls.msg = "Unexpected {0} value received. Expected: {1}," \
                  "Received: {2}, Reason: {3}, Contents: {4}"

        cls.url = cls.stacktach_config.db_url
        cls.serializer = cls.marshalling.serializer
        cls.deserializer = cls.marshalling.deserializer

        cls.stacktach_dbclient = StackTachDBClient(cls.url, cls.serializer,
                                                   cls.deserializer)
        cls.stacktach_db_behavior = StackTachDBBehavior(cls.stacktach_dbclient,
                                                        cls.stacktach_config)

    @classmethod
    def stacktach_events_for_server(cls, server):
        """
        @summary: Connects to StackTach DB to obtain
        relevant validation data for a server.
        @param server: Server details.
        @type server: Server
        """
        cls.launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=server.id))
        cls.event_launches = sorted(cls.launch_response.entity,
                                    key=lambda launch: launch.id_)
        cls.event_launch = cls.event_launches[0]

        cls.delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=server.id))
        cls.event_delete = None
        if cls.delete_response.entity:
            cls.event_delete = cls.delete_response.entity[0]

        cls.exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=server.id))
        cls.event_exist = None
        if cls.exist_response.entity:
            cls.event_exists = sorted(cls.exist_response.entity,
                                      key=lambda exist: exist.id_)
            cls.event_exist = cls.event_exists[0]


class StackTachComputeIntegration(ComputeFixture, StackTachDBFixture):

    @classmethod
    def create_server(cls, name=None, image_ref=None, flavor_ref=None,
                      personality=None, metadata=None, disk_config=None,
                      networks=None):
        """
        @summary: Creates a server using defaults from the test data,
            waits for active state.
        @param name: The name of the server.
        @type name: String
        @param image_ref: The reference to the image used to build the server.
        @type image_ref: String
        @param flavor_ref: The flavor used to build the server.
        @type flavor_ref: String
        @param personality: A list of dictionaries for files to be injected
            into the server.
        @type personality: List
        @param metadata: A dictionary of values to be used as metadata.
        @type metadata: Dictionary. The limit is 5 key/values.
        @param disk_config: MANUAL/AUTO/None
        @type disk_config: String
        @param networks:The networks to which you want to attach the server.
        @type networks: String
        """
        super(StackTachComputeIntegration, cls).setUpClass()

        if name is None:
            name = rand_name('testservercc')
        if image_ref is None:
            image_ref = cls.image_ref
        if flavor_ref is None:
            flavor_ref = cls.flavor_ref

        create_response = (cls.servers_client
                           .create_server(name=name,
                                          image_ref=image_ref,
                                          flavor_ref=flavor_ref,
                                          personality=personality,
                                          metadata=metadata,
                                          disk_config=disk_config,
                                          networks=networks))

        cls.expected_audit_period_beginning = \
            datetime.utcnow().strftime(Constants.DATETIME_0AM_FORMAT)
        cls.expected_audit_period_ending = \
            ((datetime.utcnow() + timedelta(days=1))
             .strftime(Constants.DATETIME_0AM_FORMAT))

        cls.created_server = create_response.entity
        if cls.created_server is None:
            raise Exception("Server Create failed with response code: {0}."
                            "Response: {1}".format(create_response.status_code,
                                                   create_response))

        cls.resources.add(cls.created_server.id,
                          cls.servers_client.delete_server)

        wait_response = (cls.server_behaviors
                         .wait_for_server_status(cls.created_server.id,
                                                 ServerStates.ACTIVE))
        wait_response.entity.admin_pass = cls.created_server.admin_pass

        cls.launched_at_created_server = \
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT)
        cls.stacktach_db_behavior.wait_for_launched_at(
            server_id=cls.created_server.id,
            interval_time=cls.servers_config.server_status_interval,
            timeout=cls.servers_config.server_build_timeout)

        cls.created_server = wait_response.entity

    @classmethod
    def resize_server(cls, resize_flavor=None):
        """
        @summary: Performs a resize on the created server and waits for
            verify_resize state.
        @param resize_flavor: Flavor to which Server needs to be resized.
        @type resize_flavor: String
        """
        cls.resize_flavor = cls.flavor_ref_alt
        if resize_flavor is not None:
            cls.resize_flavor = resize_flavor

        cls.servers_client.resize(server_id=cls.created_server.id,
                                  flavorRef=cls.resize_flavor)
        cls.resize_start_time = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))

        wait_response = (cls.server_behaviors.wait_for_server_status(
            cls.created_server.id,
            ServerStates.VERIFY_RESIZE))

        cls.launched_at_resized_server = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))
        cls.stacktach_db_behavior.wait_for_launched_at(
            server_id=cls.created_server.id,
            interval_time=cls.servers_config.server_status_interval,
            timeout=cls.servers_config.server_build_timeout)

        cls.verify_resized_server = wait_response.entity

    @classmethod
    def confirm_resize_server(cls):
        """
        @summary: Performs a confirm resize on the created server.
            Connects to StackTach DB to obtain relevant validation data.
        """
        cls.servers_client.confirm_resize(cls.created_server.id)
        cls.confirm_resize_start_time = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))
        wait_response = (cls.server_behaviors
                         .wait_for_server_status(cls.created_server.id,
                                                 ServerStates.ACTIVE))
        cls.launched_at_confirm_resize_server = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))

        cls.stacktach_db_behavior.wait_for_launched_at(
            server_id=cls.created_server.id,
            interval_time=cls.servers_config.server_status_interval,
            timeout=cls.servers_config.server_build_timeout)

        cls.confirmed_resized_server = wait_response.entity

    @classmethod
    def revert_resize_server(cls):
        """
        @summary: Performs a revert resize on the created server
            and waits for active state.  Connects to StackTach DB to obtain
            relevant validation data.
        """
        cls.servers_client.revert_resize(cls.created_server.id)
        cls.revert_resize_start_time = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))

        wait_response = cls.server_behaviors \
            .wait_for_server_status(cls.created_server.id,
                                    ServerStates.ACTIVE)
        cls.launched_at_revert_resize_server = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))

        cls.stacktach_db_behavior.wait_for_launched_at(
            server_id=cls.created_server.id,
            interval_time=cls.servers_config.server_status_interval,
            timeout=cls.servers_config.server_build_timeout)

        cls.reverted_resized_server = wait_response.entity

    @classmethod
    def rebuild_server(cls, rebuild_image_ref=None):
        """
        @summary: Performs a  rebuild on the created server using the
            configured secondary image and waits for the active state.
            Connects to StackTach DB to obtain relevant validation data.
        @param rebuild_image_ref: The reference to the image used to
            rebuild the server.
        @type rebuild_image_ref: String
        """
        cls.rebuild_image_ref = cls.image_ref_alt
        if rebuild_image_ref:
            cls.rebuild_image_ref = rebuild_image_ref

        rebuild_response = cls.servers_client.rebuild(
            server_id=cls.created_server.id,
            image_ref=cls.rebuild_image_ref)
        cls.rebuild_start_time = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))
        wait_response = (cls.server_behaviors
                         .wait_for_server_status(cls.created_server.id,
                                                 ServerStates.ACTIVE))

        cls.launched_at_rebuilt_server = (datetime.utcnow()
                                          .strftime(Constants
                                                    .DATETIME_FORMAT))
        cls.stacktach_db_behavior.wait_for_launched_at(
            server_id=cls.created_server.id,
            interval_time=cls.servers_config.server_status_interval,
            timeout=cls.servers_config.server_build_timeout)

        cls.rebuilt_server = wait_response.entity
        cls.rebuilt_server.admin_pass = rebuild_response.entity.admin_pass

    @classmethod
    def rescue_and_unrescue_server(cls):
        """
        @summary: Rescue instance and waits for server status RESCUE.
            Then unrescues the instance and waits for server status ACTIVE.
            Connects to StackTach DB to obtain relevant validation data.
        """
        cls.rescue_client.rescue(server_id=cls.created_server.id)
        cls.rescue_start_time = (datetime.utcnow().strftime(Constants
                                 .DATETIME_FORMAT))
        cls.server_behaviors.wait_for_server_status(cls.created_server.id,
                                                    ServerStates.RESCUE)

        cls.rescue_client.unrescue(server_id=cls.created_server.id)
        wait_response = (cls.server_behaviors
                         .wait_for_server_status(cls.created_server.id,
                                                 ServerStates.ACTIVE))

        cls.launched_at_unrescued_server = (datetime.utcnow()
                                            .strftime(Constants
                                                      .DATETIME_FORMAT))
        cls.stacktach_db_behavior.wait_for_launched_at(
            server_id=cls.created_server.id,
            interval_time=cls.servers_config.server_status_interval,
            timeout=cls.servers_config.server_build_timeout)

        cls.unrescued_server = wait_response.entity

    @classmethod
    def hard_reboot_server(cls):
        """
        @summary: Performs a hard reboot on the created server and waits for
            the active state. Connects to StackTach DB to obtain relevant
            validation data.
        """
        cls.servers_client.reboot(cls.created_server.id, RebootTypes.HARD)
        wait_response = (cls.server_behaviors
                         .wait_for_server_status(cls.created_server.id,
                                                 ServerStates.ACTIVE))

        cls.launched_at_hard_rebooted_server = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))

        cls.hard_rebooted_server = wait_response.entity

    @classmethod
    def soft_reboot_server(cls):
        """
        @summary: Performs a soft reboot on the created server and waits for
            the active state. Connects to StackTach DB to obtain
            relevant validation data.
        """
        cls.servers_client.reboot(cls.created_server.id, RebootTypes.SOFT)
        wait_response = (cls.server_behaviors
                         .wait_for_server_status(cls.created_server.id,
                                                 ServerStates.ACTIVE))

        cls.launched_at_soft_rebooted_server = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))

        cls.soft_rebooted_server = wait_response.entity

    @classmethod
    def change_password_server(cls):
        """
        @summary: Performs a change password on the created server and waits
            for the active state. Connects to StackTach DB to obtain
            relevant validation data.
        """
        cls.new_password = "newslice129690TuG72Bgj2"
        cls.changed_password_server = (
            cls.server_behaviors.change_password_and_await(
                server_id=cls.created_server.id,
                new_password=cls.new_password))

    @classmethod
    def delete_server(cls):
        """
        @summary: Performs a delete on the created server and waits for
            the deleted state. Connects to StackTach DB to obtain
            relevant validation data.
        """

        wait_response = (cls.servers_client
                         .get_server(cls.created_server.id))
        cls.servers_client.delete_server(cls.created_server.id)

        cls.server_behaviors.wait_for_server_to_be_deleted(
            cls.created_server.id)
        cls.deleted_at = (
            datetime.utcnow().strftime(Constants.DATETIME_FORMAT))

        cls.deleted_server = wait_response.entity


class StackTachTestAssertionsFixture(StackTachDBFixture):

    def validate_attributes_in_launch_response(self, num_of_launch_entry=1):
        """
        @summary: Validates that all the attributes of
            launch response is either Not Null or None as
            expected
        @param num_of_launch_entry: No. of expected launch entries
        @type num_of_launch_entry: Int
        """
        self.assertEqual(len(self.launch_response.entity),
                         num_of_launch_entry,
                         self.msg.format("List of Launch objects",
                                         num_of_launch_entry,
                                         len(self.launch_response.entity),
                                         self.launch_response.reason,
                                         self.launch_response.content))
        self.assertTrue(self.launch_response.ok,
                        self.msg.format("status_code", 200,
                                        self.launch_response.status_code,
                                        self.launch_response.reason,
                                        self.launch_response.content))
        validation_entities = ["id_", "request_id", "instance", "launched_at",
                               "instance_type_id", "instance_flavor_id",
                               "tenant", "os_distro", "os_version",
                               "os_architecture", "rax_options"]
        for launch in self.event_launches:
            for entity in validation_entities:
                self.assertTrue(getattr(launch, entity),
                                self.msg.format(entity,
                                                "Not None or Empty",
                                                getattr(launch, entity),
                                                self.launch_response.reason,
                                                self.launch_response.content))

    def validate_launch_entry_field_values(self, server,
                                           event_launch_server=None,
                                           expected_flavor_ref=None,
                                           launched_at=None):
        """
        @summary: Validate that the Launch entry will have all expected values
        @param server: Details of the server created in test
        @type server: Server
        @param event_launch_server: Details of the event Launch from DB
        @type event_launch_server: ServerLaunch
        @param expected_flavor_ref: The expected flavor to verify against
        @type expected_flavor_ref: String
        @param launched_at: The launched_at time of the server
        @type launched_at: datetime
        """
        self.event_launch_server = self.event_launch
        if event_launch_server:
            self.event_launch_server = event_launch_server

        self.expected_flavor_ref = self.flavor_ref
        if expected_flavor_ref:
            self.expected_flavor_ref = expected_flavor_ref

        self.launched_at = self.launched_at_created_server
        if launched_at:
            self.launched_at = launched_at

        self.assertEqual(server.id,
                         self.event_launch_server.instance,
                         self.msg.format(
                             "instance",
                             server.id,
                             self.event_launch_server.instance,
                             self.launch_response.reason,
                             self.launch_response.content))
        self.assertEqual(server.flavor.id,
                         self.event_launch_server.instance_type_id,
                         self.msg.format(
                             "instance_type_id",
                             server.flavor.id,
                             self.event_launch_server.instance_type_id,
                             self.launch_response.reason,
                             self.launch_response.content))
        self.assertEqual(self.expected_flavor_ref,
                         self.event_launch_server.instance_type_id,
                         self.msg.format(
                             "instance_type_id",
                             self.expected_flavor_ref,
                             self.event_launch_server.instance_type_id,
                             self.launch_response.reason,
                             self.launch_response.content))
        self.assertEqual(self.expected_flavor_ref,
                         self.event_launch_server.instance_flavor_id,
                         self.msg.format(
                             "instance_flavor_id",
                             self.expected_flavor_ref,
                             self.event_launch_server.instance_flavor_id,
                             self.launch_response.reason,
                             self.launch_response.content))
        self.assertTrue(
            EqualityTools.are_datetimes_equal(
                string_to_datetime(self.launched_at),
                string_to_datetime(self.event_launch_server.launched_at),
                timedelta(seconds=self.leeway)),
            self.msg.format("launched_at",
                            self.launched_at,
                            self.event_launch_server.launched_at,
                            self.launch_response.reason,
                            self.launch_response.content))

    def validate_attributes_in_exist_response(self, num_of_exist_entry=1):
        """
        @summary: Validates that all the attributes of
            exist response is either Not Null or None as
            expected
        @param num_of_exist_entry: No. of expected exist entries
        @type num_of_exist_entry: Int
        """
        self.assertEqual(len(self.exist_response.entity),
                         num_of_exist_entry,
                         self.msg.format("List of Exists objects",
                                         num_of_exist_entry,
                                         len(self.exist_response.entity),
                                         self.exist_response.reason,
                                         self.exist_response.content))
        self.assertTrue(self.exist_response.ok,
                        self.msg.format("status_code", 200,
                                        self.exist_response.status_code,
                                        self.exist_response.reason,
                                        self.exist_response.content))
        validation_entities = ["id_", "instance", "audit_period_beginning",
                               "audit_period_ending", "launched_at",
                               "message_id", "raw", "instance_type_id",
                               "instance_flavor_id", "status", "usage",
                               "tenant", "os_distro", "os_version",
                               "os_architecture", "rax_options"]
        # We do not delete the server so deleted_at and delete
        # should be null.
        validate_none_entities = ["deleted_at", "delete", "fail_reason"]
        validate_not_none_entities = ["send_status", "bandwidth_public_out"]
        for exist in self.event_exists:
            for entity in validation_entities:
                self.assertTrue(getattr(exist, entity),
                                self.msg.format(entity,
                                                "Not None or Empty",
                                                getattr(exist, entity),
                                                self.exist_response.reason,
                                                self.exist_response.content))
            for entity in validate_none_entities:
                self.assertIsNone(getattr(exist, entity),
                                  self.msg.format(entity,
                                                  "None or Empty",
                                                  getattr(exist, entity),
                                                  self.exist_response.reason,
                                                  self.exist_response.content))
            for entity in validate_not_none_entities:
                self.assertIsNotNone(
                    getattr(exist, entity),
                    self.msg.format(entity,
                                    "Not None or Empty",
                                    getattr(exist, entity),
                                    self.exist_response.reason,
                                    self.exist_response.content))

    def validate_exist_entry_field_values(self, server,
                                          event_exist_server=None,
                                          expected_flavor_ref=None,
                                          launched_at=None):
        """
        @summary: Validate that the Exist entry will have all expected values
        @param server: Details of the server created in test
        @type server: Server
        @param event_exist_server: Details of the event Exist from DB
        @type event_exist_server: ServerExists
        @param expected_flavor_ref: The expected flavor to verify against
        @type expected_flavor_ref: String
        @param launched_at: The launched_at time of the server
        @type launched_at: datetime
        """

        self.event_exist_server = self.event_exist
        if event_exist_server:
            self.event_exist_server = event_exist_server

        self.expected_flavor_ref = self.flavor_ref
        if expected_flavor_ref:
            self.expected_flavor_ref = expected_flavor_ref

        self.launched_at = self.launched_at_created_server
        if launched_at:
            self.launched_at = launched_at

        self.assertEqual(server.id, self.event_exist_server.instance,
                         self.msg.format("instance",
                                         self.created_server.id,
                                         self.event_exist_server.instance,
                                         self.exist_response.reason,
                                         self.exist_response.content))
        self.assertEqual(server.flavor.id,
                         self.event_exist_server.instance_type_id,
                         self.msg.format(
                             "instance_type_id",
                             self.created_server.flavor.id,
                             self.event_exist_server.instance_type_id,
                             self.exist_response.reason,
                             self.exist_response.content))
        self.assertEqual(self.expected_flavor_ref,
                         self.event_exist_server.instance_type_id,
                         self.msg.format(
                             "instance_type_id",
                             self.expected_flavor_ref,
                             self.event_exist_server.instance_type_id,
                             self.exist_response.reason,
                             self.exist_response.content))
        self.assertEqual(self.expected_flavor_ref,
                         self.event_exist_server.instance_flavor_id,
                         self.msg.format(
                             "instance_flavor_id",
                             self.expected_flavor_ref,
                             self.event_exist_server.instance_flavor_id,
                             self.exist_response.reason,
                             self.exist_response.content))
        self.assertIn(self.event_exist_server.status, ['pending', 'verified'],
                      self.msg.format("status",
                                      "Not None, Empty or unexpected value",
                                      self.event_exist_server.status,
                                      self.exist_response.reason,
                                      self.exist_response.content))
        self.assertIn(self.event_exist_server.send_status, [0, 201],
                      self.msg.format("send_status",
                                      "Not None, Empty or unexpected value",
                                      self.event_exist_server.status,
                                      self.exist_response.reason,
                                      self.exist_response.content))
        self.assertTrue(
            EqualityTools.are_datetimes_equal(
                string_to_datetime(self.launched_at),
                string_to_datetime(self.event_exist_server.launched_at),
                timedelta(seconds=self.leeway)),
            self.msg.format("launched_at",
                            self.launched_at,
                            self.event_exist_server.launched_at,
                            self.exist_response.reason,
                            self.exist_response.content))

    def validate_exist_entry_audit_period_values(
            self, expected_audit_period_ending,
            expected_audit_period_beginning, event_exist_server=None):
        """
        @summary: Validate that the Exist entry will have all expected values
         related to audit periods
        @param expected_audit_period_ending: The expected audit period ending
            of the server
        @type expected_audit_period_ending: datetime
        @param expected_audit_period_beginning: The expected audit period
            beginning of the server
        @type expected_audit_period_beginning: datetime
        @param event_exist_server: Details of the event Exist from DB
        @type event_exist_server: ServerExists
        """
        self.event_exist_server = self.event_exist
        if event_exist_server:
            self.event_exist_server = event_exist_server

        self.assertTrue(EqualityTools.are_datetimes_equal(
            string_to_datetime(expected_audit_period_ending),
            string_to_datetime(self.event_exist_server.audit_period_ending),
            timedelta(seconds=self.leeway)))
        self.assertTrue(EqualityTools.are_datetimes_equal(
            string_to_datetime(expected_audit_period_beginning),
            string_to_datetime(self.event_exist_server.audit_period_beginning),
            timedelta(seconds=self.leeway)))
        self.assertTrue(EqualityTools.are_datetimes_equal(
            string_to_datetime(expected_audit_period_ending),
            string_to_datetime(self.event_exist_server.received),
            timedelta(seconds=self.leeway)))

    def validate_no_exists_entry_returned(self):
        """
        @summary: Validate that there is no exist entry found
        """
        self.assertTrue(self.exist_response.ok,
                        self.msg.format("status_code",
                                        200,
                                        self.exist_response.status_code,
                                        self.exist_response.reason,
                                        self.exist_response.content))
        self.assertFalse(self.event_exist,
                         self.msg.format("Non-empty List of Exist objects",
                                         "Empty List", self.event_exist,
                                         self.exist_response.reason,
                                         self.exist_response.content))

    def validate_no_deletes_entry_returned(self):
        """
        @summary: Validate that there is no delete entry found
            as the server hasn't been deleted yet
        """
        self.assertTrue(self.delete_response.ok,
                        self.msg.format("status_code",
                                        200,
                                        self.delete_response.status_code,
                                        self.delete_response.reason,
                                        self.delete_response.content))
        self.assertFalse(self.event_delete,
                         self.msg.format("Non-empty List of Delete objects",
                                         "Empty List", self.event_delete,
                                         self.delete_response.reason,
                                         self.delete_response.content))
