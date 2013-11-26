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

        cls.url = cls.stacktach_config.db_url
        cls.serializer = cls.marshalling.serializer
        cls.deserializer = cls.marshalling.deserializer

        cls.stacktach_dbclient = StackTachDBClient(cls.url, cls.serializer,
                                                   cls.deserializer)
        cls.stacktach_db_behavior = StackTachDBBehavior(cls.stacktach_dbclient,
                                                        cls.stacktach_config)


class CreateServerFixture(ComputeFixture, StackTachDBFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state.
    """
    @classmethod
    def setUpClass(cls):
        super(CreateServerFixture, cls).setUpClass()

        cls.created_server = cls.servers_client.create_server()
        cls.expected_audit_period_beginning = \
            datetime.utcnow().strftime(Constants.DATETIME_0AM_FORMAT)
        cls.expected_audit_period_ending = \
            ((datetime.utcnow() + timedelta(days=1))
             .strftime(Constants.DATETIME_0AM_FORMAT))
        try:
            wait_response = (cls.server_behaviors
                             .wait_for_server_status(cls.created_server.id,
                                                     ServerStates.ACTIVE))
            wait_response.entity.adminPass = cls.created_server.adminPass
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
        cls.created_server = cls.wait_response.entity


class StackTachCreateServerFixture(CreateServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Connects to StackTach DB to obtain
        relevant validation data.
    """
    @classmethod
    def setUpClass(cls):
        super(StackTachCreateServerFixture, cls).setUpClass()
        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.created_server.id))
        cls.st_launch_created_server = cls.st_launch_response.entity[0]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.created_server.id))
        cls.st_delete = cls.st_delete_response.entity
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.created_server.id))
        cls.st_exist = cls.st_exist_response.entity


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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, resize_flavor=None):

        super(ResizeServerFixture, cls).setUpClass(name=name,
                                                   imageRef=imageRef,
                                                   flavorRef=flavorRef,
                                                   personality=personality,
                                                   metadata=metadata,
                                                   disk_config=disk_config,
                                                   networks=networks)
        if resize_flavor is not None:
            cls.resize_flavor = resize_flavor
        else:
            cls.resize_flavor = cls.flavor_ref_alt
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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, resize_flavor=None):

        super(ConfirmResizeServerFixture, cls).setUpClass(
            name=name,
            imageRef=imageRef,
            flavorRef=flavorRef,
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


class StackTachConfirmResizeServerFixture(ConfirmResizeServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Then Resizes and Confirms the
        Resize of the server. Connects to StackTach DB to obtain
        relevant validation data.
    """

    @classmethod
    def setUpClass(cls, flavorRef=None, resize_flavor=None):

        super(StackTachConfirmResizeServerFixture, cls).setUpClass(
            flavorRef=flavorRef, resize_flavor=resize_flavor)

        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.confirmed_resized_server.id))
        cls.st_launches = sorted(cls.st_launch_response.entity,
                                 key=lambda launch: launch.id)
        cls.st_launch_create_server = cls.st_launches[0]
        cls.st_launch_resize_server = cls.st_launches[1]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.confirmed_resized_server.id))
        cls.st_delete = cls.st_delete_response.entity
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.confirmed_resized_server.id))
        cls.st_exist = cls.st_exist_response.entity[0]


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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, resize_flavor=None):

        super(RevertResizeServerFixture, cls).setUpClass(
            name=name,
            imageRef=imageRef,
            flavorRef=flavorRef,
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


class StackTachRevertResizeServerFixture(RevertResizeServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Then resizes the server and revert
        resizes the server. Connects to StackTach DB to obtain
        relevant validation data.
    """

    @classmethod
    def setUpClass(cls, flavorRef=None, resize_flavor=None):

        super(StackTachRevertResizeServerFixture, cls).setUpClass(
            flavorRef=flavorRef, resize_flavor=resize_flavor)

        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.reverted_resized_server.id))
        cls.st_launches = sorted(cls.st_launch_response.entity,
                                 key=lambda launch: launch.id)
        cls.st_launch_create_server = cls.st_launches[0]
        cls.st_launch_resize_server = cls.st_launches[1]
        cls.st_launch_revert_resize = cls.st_launches[2]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.reverted_resized_server.id))
        cls.st_delete = cls.st_delete_response.entity
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.reverted_resized_server.id))
        cls.st_exists = sorted(cls.st_exist_response.entity,
                               key=lambda exist: exist.id)
        cls.st_exist_resize_server = cls.st_exists[0]
        cls.st_exist_revert_resize_server = cls.st_exists[1]


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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None, rebuild_image_ref=None):
        super(RebuildServerFixture, cls).setUpClass(name=name,
                                                    imageRef=imageRef,
                                                    flavorRef=flavorRef,
                                                    personality=personality,
                                                    metadata=metadata,
                                                    disk_config=disk_config,
                                                    networks=networks)
        if rebuild_image_ref is None:
            cls.rebuild_image_ref = cls.image_ref_alt
        else:
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


class StackTachRebuildServerFixture(RebuildServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Then rebuilds the server.
        Connects to StackTach DB to obtain relevant validation data.
    """
    @classmethod
    def setUpClass(cls):
        super(StackTachRebuildServerFixture, cls).setUpClass()

        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.rebuilt_server.id))
        cls.st_launches = sorted(cls.st_launch_response.entity,
                                 key=lambda launch: launch.id)
        cls.st_launch_created_server = cls.st_launches[0]
        cls.st_launch_rebuilt_server = cls.st_launches[1]
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.rebuilt_server.id))
        cls.st_exist = cls.st_exist_response.entity[0]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.rebuilt_server.id))
        cls.st_delete = cls.st_delete_response.entity


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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):

        super(HardRebootServerFixture, cls).setUpClass(name=name,
                                                       imageRef=imageRef,
                                                       flavorRef=flavorRef,
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
            cls.reboot_response = wait_response
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)
        cls.hard_rebooted_server = wait_response.entity


class StackTachHardRebootServerFixture(HardRebootServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Then hard reboots the server.
        Connects to StackTach DB to obtain relevant validation data.
    """

    @classmethod
    def setUpClass(cls):

        super(StackTachHardRebootServerFixture, cls).setUpClass()

        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.hard_rebooted_server.id))
        cls.st_launch_create_server = cls.st_launch_response.entity[0]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.hard_rebooted_server.id))
        cls.st_delete = cls.st_delete_response.entity
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.hard_rebooted_server.id))
        cls.st_exist = cls.st_exist_response.entity


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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):

        super(SoftRebootServerFixture, cls).setUpClass(name=name,
                                                       imageRef=imageRef,
                                                       flavorRef=flavorRef,
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
            cls.reboot_response = wait_response
        except (TimeoutException, BuildErrorException) as exception:
            cls.assertClassSetupFailure(exception.message)
        cls.soft_rebooted_server = wait_response.entity


class StackTachSoftRebootServerFixture(SoftRebootServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Then soft reboots the server.
        Connects to StackTach DB to obtain relevant validation data.
    """

    @classmethod
    def setUpClass(cls):

        super(StackTachSoftRebootServerFixture, cls).setUpClass()

        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.soft_rebooted_server.id))
        cls.st_launch_create_server = cls.st_launch_response.entity[0]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.soft_rebooted_server.id))
        cls.st_delete = cls.st_delete_response.entity
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.soft_rebooted_server.id))
        cls.st_exist = cls.st_exist_response.entity


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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):
        super(ChangePasswordServerFixture, cls).setUpClass(
            name=name,
            imageRef=imageRef,
            flavorRef=flavorRef,
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


class StackTachChangePasswordServerFixture(ChangePasswordServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Changes password on server.
        Connects to StackTach DB to obtain relevant validation data.
    """

    @classmethod
    def setUpClass(cls):
        super(StackTachChangePasswordServerFixture, cls).setUpClass()
        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.changed_password_server.id))
        cls.st_launch = cls.st_launch_response.entity[0]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.changed_password_server.id))
        cls.st_delete = cls.st_delete_response.entity
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.changed_password_server.id))
        cls.st_exist = cls.st_exist_response.entity


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
    def setUpClass(cls, name=None, imageRef=None, flavorRef=None,
                   personality=None, metadata=None, disk_config=None,
                   networks=None):

        super(DeleteServerFixture, cls).setUpClass(name=name,
                                                   imageRef=imageRef,
                                                   flavorRef=flavorRef,
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


class StackTachDeleteServerFixture(DeleteServerFixture):
    """
    @summary: Creates a server using defaults from the test data,
        waits for active state. Then deletes the server.
        Connects to StackTach DB to obtain relevant validation data.
    """

    @classmethod
    def setUpClass(cls):

        super(StackTachDeleteServerFixture, cls).setUpClass()

        cls.st_launch_response = (
            cls.stacktach_db_behavior.list_launches_for_uuid(
                instance=cls.deleted_server.id))
        cls.st_launch_create_server = cls.st_launch_response.entity[0]
        cls.st_delete_response = (
            cls.stacktach_db_behavior.list_deletes_for_uuid(
                instance=cls.deleted_server.id))
        cls.st_delete = cls.st_delete_response.entity[0]
        cls.st_exist_response = (
            cls.stacktach_db_behavior.list_exists_for_uuid(
                instance=cls.deleted_server.id))
        cls.st_exist = cls.st_exist_response.entity
