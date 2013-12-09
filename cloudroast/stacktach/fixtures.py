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
from cloudcafe.compute.common.constants import Constants
from cloudcafe.compute.common.exceptions import TimeoutException,\
    BuildErrorException
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates, NovaServerRebootTypes as RebootTypes
from cloudcafe.stacktach.config import StacktachConfig, MarshallingConfig
from cloudcafe.stacktach.stacktach_db_api.behaviors import StackTachDBBehavior
from cloudcafe.stacktach.stacktach_db_api.client import StackTachDBClient
from cloudcafe.stacktach.stacky_api.client import StackTachClient
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
        cls.event_id = cls.stacktach_config.event_id
        cls.days_passed = cls.stacktach_config.days_passed
        cls.msg = "Unexpected {0} value received. Expected: {1}," \
                  "Received: {2}, Reason: {3}, Contents: {4}"

        cls.url = cls.stacktach_config.url
        cls.serializer = cls.marshalling.serializer
        cls.deserializer = cls.marshalling.deserializer

        cls.stacktach_client = StackTachClient(cls.url, cls.serializer,
                                               cls.deserializer)


class StackTachDBFixture(BaseTestFixture):
    """
    @summary: Fixture for any StackTachDB test.
    """
    @classmethod
    def setUpClass(cls):
        super(StackTachDBFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.stacktach_config = StacktachConfig()
        cls.event_id = cls.stacktach_config.event_id
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
        if cls.delete_response.entity:
            cls.event_delete = cls.delete_response.entity[0]
        else:
            cls.event_delete = cls.delete_response.entity

        cls.exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=server.id))
        if cls.exist_response.entity:
            cls.event_exists = sorted(cls.exist_response.entity,
                                      key=lambda exist: exist.id_)
            cls.event_exist = cls.event_exists[0]
        else:
            cls.event_exist = cls.exist_response.entity


class CreateServerFixture(ComputeFixture, StackTachDBFixture):
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
    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):
        super(CreateServerFixture, cls).setUpClass()

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

        cls.created_server = create_response.entity
        try:
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
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)
        finally:
            cls.resources.add(cls.created_server.id,
                              cls.servers_client.delete_server)

        cls.created_server = wait_response.entity


class ResizeServerFixture(CreateServerFixture):
    """
    @summary: Create an active server, resizes it and waits for
        verify_resize state.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks:The networks to which you want to attach the server.
    @type networks: String
    @param resize_flavor: Flavor to which Server needs to be resized.
    @type resize_flavor: String
    """

    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, resize_flavor=None):

        super(ResizeServerFixture, cls).setUpClass(name=name,
                                                   image_ref=image_ref,
                                                   flavor_ref=flavor_ref,
                                                   personality=personality,
                                                   metadata=metadata,
                                                   disk_config=disk_config,
                                                   networks=networks)
        cls.resize_flavor = cls.flavor_ref_alt
        if resize_flavor is not None:
            cls.resize_flavor = resize_flavor

        try:
            cls.servers_client.resize(server_id=cls.created_server.id,
                                      flavorRef=cls.resize_flavor)
            cls.start_time_wait_resp_at_resize = (
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

        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

        cls.verify_resized_server = wait_response.entity


class ConfirmResizeServerFixture(ResizeServerFixture):
    """
    @summary: Create an active server, resizes it and confirms resize.
        Connects to StackTach DB to obtain relevant validation data.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks:The networks to which you want to attach the server.
    @type networks: String
    @param resize_flavor: Flavor to which Server needs to be resized.
    @type resize_flavor: String
    """

    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, resize_flavor=None):

        super(ConfirmResizeServerFixture, cls).setUpClass(
            name=name,
            image_ref=image_ref,
            flavor_ref=flavor_ref,
            personality=personality,
            metadata=metadata,
            disk_config=disk_config,
            networks=networks,
            resize_flavor=resize_flavor)

        try:
            cls.servers_client.confirm_resize(cls.created_server.id)
            wait_response = (cls.server_behaviors
                             .wait_for_server_status(cls.created_server.id,
                                                     ServerStates.ACTIVE))

            cls.stacktach_db_behavior.wait_for_launched_at(
                server_id=cls.created_server.id,
                interval_time=cls.servers_config.server_status_interval,
                timeout=cls.servers_config.server_build_timeout)
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

        cls.confirmed_resized_server = wait_response.entity


class RevertResizeServerFixture(ResizeServerFixture):
    """
    @summary: Creates a server, resizes the server, reverts the resize and
        waits for active state.  Connects to StackTach DB to obtain relevant
        validation data.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks:The networks to which you want to attach the server.
    @type networks: String
    @param resize_flavor: Flavor to which Server needs to be resized.
    @type resize_flavor: String
    """

    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, resize_flavor=None):

        super(RevertResizeServerFixture, cls).setUpClass(
            name=name,
            image_ref=image_ref,
            flavor_ref=flavor_ref,
            personality=personality,
            metadata=metadata,
            disk_config=disk_config,
            networks=networks,
            resize_flavor=resize_flavor)
        try:
            cls.servers_client.revert_resize(cls.created_server.id)
            wait_response = cls.server_behaviors\
                .wait_for_server_status(cls.created_server.id,
                                        ServerStates.ACTIVE)

            cls.launched_at_revert_resize_server = (
                datetime.utcnow().strftime(Constants.DATETIME_FORMAT))
            cls.stacktach_db_behavior.wait_for_launched_at(
                server_id=cls.created_server.id,
                interval_time=cls.servers_config.server_status_interval,
                timeout=cls.servers_config.server_build_timeout)
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

        cls.reverted_resized_server = wait_response.entity


class RebuildServerFixture(CreateServerFixture):
    """
    @summary: Creates an Active server, Rebuilds the server using the
        configured secondary image and waits for the active state.
        Connects to StackTach DB to obtain relevant validation data.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks:The networks to which you want to attach the server.
    @type networks: String
    @param rebuild_image_ref: The reference to the image used to
        rebuild the server.
    @type rebuild_image_ref: String
    """
    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, rebuild_image_ref=None):
        super(RebuildServerFixture, cls).setUpClass(name=name,
                                                    image_ref=image_ref,
                                                    flavor_ref=flavor_ref,
                                                    personality=personality,
                                                    metadata=metadata,
                                                    disk_config=disk_config,
                                                    networks=networks)
        cls.rebuild_image_ref = cls.image_ref_alt
        if rebuild_image_ref:
            cls.rebuild_image_ref = rebuild_image_ref

        try:
            cls.servers_client.rebuild(server_id=cls.created_server.id,
                                       image_ref=cls.rebuild_image_ref)
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
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

        cls.rebuilt_server = wait_response.entity


class HardRebootServerFixture(CreateServerFixture):
    """
    @summary: Performs a hard reboot on the created server and waits for the
        active state. Connects to StackTach DB to obtain relevant
        validation data.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks:The networks to which you want to attach the server.
    @type networks: String
    """

    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):

        super(HardRebootServerFixture, cls).setUpClass(name=name,
                                                       image_ref=image_ref,
                                                       flavor_ref=flavor_ref,
                                                       personality=personality,
                                                       metadata=metadata,
                                                       disk_config=disk_config,
                                                       networks=networks)

        try:
            cls.servers_client.reboot(cls.created_server.id, RebootTypes.HARD)
            wait_response = (cls.server_behaviors
                             .wait_for_server_status(cls.created_server.id,
                                                     ServerStates.ACTIVE))

            cls.launched_at_hard_rebooted_server = (
                datetime.utcnow().strftime(Constants.DATETIME_FORMAT))
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

        cls.hard_rebooted_server = wait_response.entity


class SoftRebootServerFixture(CreateServerFixture):
    """
    @summary: Performs a soft reboot on the created server and waits for
        the active state. Connects to StackTach DB to obtain
        relevant validation data.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks:The networks to which you want to attach the server.
    @type networks: String
    """

    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):

        super(SoftRebootServerFixture, cls).setUpClass(name=name,
                                                       image_ref=image_ref,
                                                       flavor_ref=flavor_ref,
                                                       personality=personality,
                                                       metadata=metadata,
                                                       disk_config=disk_config,
                                                       networks=networks)

        try:
            cls.servers_client.reboot(cls.created_server.id, RebootTypes.SOFT)
            wait_response = (cls.server_behaviors
                             .wait_for_server_status(cls.created_server.id,
                                                     ServerStates.ACTIVE))

            cls.launched_at_soft_rebooted_server = (
                datetime.utcnow().strftime(Constants.DATETIME_FORMAT))
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

        cls.soft_rebooted_server = wait_response.entity


class ChangePasswordServerFixture(CreateServerFixture):
    """
    @summary: Performs a change password on the created server and waits for
        the active state. Connects to StackTach DB to obtain
        relevant validation data.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks:The networks to which you want to attach the server.
    @type networks: String
    """

    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):
        super(ChangePasswordServerFixture, cls).setUpClass(
            name=name,
            image_ref=image_ref,
            flavor_ref=flavor_ref,
            personality=personality,
            metadata=metadata,
            disk_config=disk_config,
            networks=networks)

        try:
            cls.new_password = "newslice129690TuG72Bgj2"
            cls.servers_client.change_password(
                server_id=cls.created_server.id, password=cls.new_password)

            wait_response = (cls.server_behaviors
                             .wait_for_server_status(cls.created_server.id,
                                                     ServerStates.ACTIVE))
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

        cls.changed_password_server = wait_response.entity


class DeleteServerFixture(CreateServerFixture):
    """
    @summary: Performs a delete on the created server and waits for
        the deleted state. Connects to StackTach DB to obtain
        relevant validation data.
    @param name: The name of the server.
    @type name: String
    @param image_ref: The reference to the image used to build the server.
    @type image_ref: String
    @param flavor_ref: The flavor used to build the server.
    @type flavor_ref: String
    @param personality: A list of dictionaries for files to be
        injected into the server.
    @type personality: List
    @param metadata: A dictionary of values to be used as metadata.
    @type metadata: Dictionary. The limit is 5 key/values.
    @param disk_config: MANUAL/AUTO/None
    @type disk_config: String
    @param networks: The networks to which you want to attach the server.
    @type networks: String
    """

    @classmethod
    def setUpClass(cls, name=None, image_ref=None, flavor_ref=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):

        super(DeleteServerFixture, cls).setUpClass(name=name,
                                                   image_ref=image_ref,
                                                   flavor_ref=flavor_ref,
                                                   personality=personality,
                                                   metadata=metadata,
                                                   disk_config=disk_config,
                                                   networks=networks)

        try:
            wait_response = (cls.servers_client
                             .get_server(cls.created_server.id))
            cls.servers_client.delete_server(cls.created_server.id)

            cls.server_behaviors.wait_for_server_to_be_deleted(
                cls.created_server.id)
            cls.deleted_at = (
                datetime.utcnow().strftime(Constants.DATETIME_FORMAT))
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)

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
        for launch in self.event_launches:
            self.assertTrue(launch.id_,
                            self.msg.format("id",
                                            "Not None or Empty", launch.id_,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.request_id,
                            self.msg.format("request_id",
                                            "Not None or Empty",
                                            launch.request_id,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.instance,
                            self.msg.format("instance",
                                            "Not None or Empty",
                                            launch.instance,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.launched_at,
                            self.msg.format("launched_at",
                                            "Not None or Empty",
                                            launch.launched_at,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.instance_type_id,
                            self.msg.format("instance_type_id",
                                            "Not None or Empty",
                                            launch.instance_type_id,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.instance_flavor_id,
                            self.msg.format("instance_flavor_id",
                                            "Not None or Empty",
                                            launch.instance_flavor_id,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.tenant,
                            self.msg.format("tenant",
                                            "Not None or Empty",
                                            launch.tenant,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.os_distro,
                            self.msg.format("os_distro",
                                            "Not None or Empty",
                                            launch.os_distro,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.os_version,
                            self.msg.format("os_version",
                                            "Not None or Empty",
                                            launch.os_version,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.os_architecture,
                            self.msg.format("os_architecture",
                                            "Not None or Empty",
                                            launch.os_architecture,
                                            self.launch_response.reason,
                                            self.launch_response.content))
            self.assertTrue(launch.rax_options,
                            self.msg.format("rax_options",
                                            "Not None or Empty",
                                            launch.rax_options,
                                            self.launch_response.reason,
                                            self.launch_response.content))

    def validate_launch_entry_field_values(self, server,
                                           event_launch_server=None,
                                           expected_flavor_ref=None):
        """
        @summary: Validate that the Launch entry will have all expected values
        @param server: Details of the server created in test
        @type server: Server
        @param event_launch_server: Details of the event Launch from DB
        @type event_launch_server: ServerLaunch
        @param expected_flavor_ref: The expected flavor to verify against
        @param expected_flavor_ref: String
        """
        self.event_launch_server = self.event_launch
        if event_launch_server:
            self.event_launch_server = event_launch_server

        self.expected_flavor_ref = self.flavor_ref
        if expected_flavor_ref:
            self.expected_flavor_ref = expected_flavor_ref

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
        for exist in self.event_exists:
            self.assertTrue(exist.id_,
                            self.msg.format("id",
                                            "Not None or Empty", exist.id_,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.instance,
                            self.msg.format("instance",
                                            "Not None or Empty",
                                            exist.instance,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.audit_period_beginning,
                            self.msg.format("audit_period_beginning",
                                            "Not None or Empty",
                                            exist.audit_period_beginning,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.audit_period_ending,
                            self.msg.format("audit_period_ending",
                                            "Not None or Empty",
                                            exist.audit_period_ending,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.launched_at,
                            self.msg.format("launched_at",
                                            "Not None or Empty",
                                            exist.launched_at,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            # We do not delete the server so deleted_at and delete
            # should be null.
            self.assertIsNone(exist.deleted_at,
                              self.msg.format("deleted_at",
                                              "None or Empty",
                                              exist.deleted_at,
                                              self.exist_response.reason,
                                              self.exist_response.content))
            self.assertIsNone(exist.delete,
                              self.msg.format("delete",
                                              "None or Empty", exist.delete,
                                              self.exist_response.reason,
                                              self.exist_response.content))
            self.assertTrue(exist.message_id,
                            self.msg.format("message_id",
                                            "Not None or Empty",
                                            exist.message_id,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.raw,
                            self.msg.format("raw",
                                            "Not None or Empty",
                                            exist.raw,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.instance_type_id,
                            self.msg.format("instance_type_id",
                                            "Not None or Empty",
                                            exist.instance_type_id,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.instance_flavor_id,
                            self.msg.format("instance_flavor_id",
                                            "Not None or Empty",
                                            exist.instance_flavor_id,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.status,
                            self.msg.format("status",
                                            "Not None or Empty",
                                            exist.status,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertIsNone(exist.fail_reason,
                              self.msg.format("fail_reason",
                                              "None or Empty",
                                              exist.fail_reason,
                                              self.exist_response.reason,
                                              self.exist_response.content))
            self.assertIsNotNone(exist.send_status,
                                 self.msg.format(
                                     "send_status",
                                     "Not None or Empty",
                                     exist.send_status,
                                     self.exist_response.reason,
                                     self.exist_response.content))
            self.assertTrue(exist.usage,
                            self.msg.format("usage",
                                            "Not None or Empty", exist.usage,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertIsNotNone(exist.bandwidth_public_out,
                                 self.msg.format(
                                     "bandwidth_public_out",
                                     "Not None or Empty",
                                     exist.bandwidth_public_out,
                                     self.exist_response.reason,
                                     self.exist_response.content))
            self.assertTrue(exist.tenant,
                            self.msg.format("tenant",
                                            "Not None or Empty",
                                            exist.tenant,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.os_distro,
                            self.msg.format("os_distro", "Not None or Empty",
                                            exist.os_distro,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.os_version,
                            self.msg.format("os_version", "Not None or Empty",
                                            exist.os_version,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.os_architecture,
                            self.msg.format("os_architecture",
                                            "Not None or Empty",
                                            exist.os_architecture,
                                            self.exist_response.reason,
                                            self.exist_response.content))
            self.assertTrue(exist.rax_options,
                            self.msg.format("rax_options", "Not None or Empty",
                                            exist.rax_options,
                                            self.exist_response.reason,
                                            self.exist_response.content))

    def validate_exist_entry_field_values(self, server,
                                          event_exist_server=None,
                                          expected_flavor_ref=None):
        """
        @summary: Validate that the Exist entry will have all expected values
        @param server: Details of the server created in test
        @type server: Server
        @param event_exist_server: Details of the event Exist from DB
        @type event_exist_server: ServerExists
        @param expected_flavor_ref: The expected flavor to verify against
        @param expected_flavor_ref: String
        """

        self.event_exist_server = self.event_exist
        if event_exist_server:
            self.event_exist_server = event_exist_server

        self.expected_flavor_ref = self.flavor_ref
        if expected_flavor_ref:
            self.expected_flavor_ref = expected_flavor_ref

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
