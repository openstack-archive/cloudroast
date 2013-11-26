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
from cloudcafe.stacktach.stacky_api.behaviors import StackTachBehavior
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

    @classmethod
    def resize_server(cls, name=None, image_ref=None, flavor_ref=None,
                      personality=None, metadata=None, disk_config=None,
                      networks=None, resize_flavor=None):
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

        cls.create_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
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

    @classmethod
    def confirm_resize_server(cls, name=None, image_ref=None,
                              flavor_ref=None, personality=None,
                              metadata=None, disk_config=None,
                              networks=None, resize_flavor=None):
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

        cls.resize_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
                          networks=networks, resize_flavor=resize_flavor)

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

    @classmethod
    def revert_resize_server(cls, name=None, image_ref=None, flavor_ref=None,
                             personality=None, metadata=None, disk_config=None,
                             networks=None, resize_flavor=None):
        """
        @summary: Creates a server, resizes the server, reverts the resize and
                  waits for active state.  Connects to StackTach DB to obtain
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
        @param resize_flavor: Flavor to which Server needs to be resized.
        @type resize_flavor: String
        """

        cls.resize_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
                          networks=networks, resize_flavor=resize_flavor)
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

    @classmethod
    def rebuild_server(cls, name=None, image_ref=None, flavor_ref=None,
                       personality=None, metadata=None, disk_config=None,
                       networks=None, rebuild_image_ref=None):
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

        cls.create_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
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

    @classmethod
    def hard_reboot_server(cls, name=None, image_ref=None, flavor_ref=None,
                           personality=None, metadata=None, disk_config=None,
                           networks=None):
        """
        @summary: Performs a hard reboot on the created server and waits for
            the active state. Connects to StackTach DB to obtain relevant
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

        cls.create_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
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

    @classmethod
    def soft_reboot_server(cls, name=None, image_ref=None, flavor_ref=None,
                           personality=None, metadata=None, disk_config=None,
                           networks=None):
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

        cls.create_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
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

    @classmethod
    def change_password_server(cls, name=None, image_ref=None, flavor_ref=None,
                               personality=None, metadata=None,
                               disk_config=None, networks=None):
        """
        @summary: Performs a change password on the created server and waits
            for the active state. Connects to StackTach DB to obtain
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
        cls.create_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
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

    @classmethod
    def delete_server(cls, name=None, image_ref=None, flavor_ref=None,
                      personality=None, metadata=None, disk_config=None,
                      networks=None):
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

        cls.create_server(name=name, image_ref=image_ref,
                          flavor_ref=flavor_ref, personality=personality,
                          metadata=metadata, disk_config=disk_config,
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
