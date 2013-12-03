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

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.stacktach.config import StacktachConfig, MarshallingConfig
from cloudcafe.stacktach.stacktach_db_api.behaviors import StackTachDBBehavior
from cloudcafe.stacktach.stacktach_db_api.client import StackTachDBClient
from cloudcafe.stacktach.stacky_api.client import StackTachClient


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
