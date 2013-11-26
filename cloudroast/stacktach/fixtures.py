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
    as ServerStates
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
                cls.created_server.id,
                interval_time=cls.servers_config.server_build_timeout,
                timeout=cls.servers_config.server_status_interval)
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
