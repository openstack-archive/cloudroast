"""
Copyright 2014 Rackspace

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

import re

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.auth.config import UserAuthConfig, UserConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.common.exception_handler import ExceptionHandler
from cloudcafe.glance.common.constants import ImageProperties, Messages
from cloudcafe.glance.config import (
    AltUserConfig, GlanceConfig, MarshallingConfig, ThirdUserConfig)
from cloudcafe.glance.behaviors import GlanceBehaviors
from cloudcafe.glance.client import GlanceClient
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.compute.fixtures import ComputeFixture


class GlanceFixture(BaseTestFixture):
    """@summary: Fixture for Glance API"""

    @classmethod
    def setUpClass(cls):
        super(GlanceFixture, cls).setUpClass()
        cls.glance_config = GlanceConfig()
        cls.marshalling = MarshallingConfig()
        cls.endpoint_config = UserAuthConfig()
        cls.user_config = UserConfig()
        cls.alt_user_config = AltUserConfig()
        cls.third_user_config = ThirdUserConfig()
        cls.resources = ResourcePool()
        cls.serialize_format = cls.marshalling.serializer
        cls.deserialize_format = cls.marshalling.deserializer

        cls.user_list = cls.generate_user_list(cls.glance_config.account_list)

        cls.access_data = cls.user_list['user'][cls.ACCESS_DATA]
        cls.glance_client = cls.user_list['user'][cls.CLIENT]
        cls.glance_behavior = cls.user_list['user'][cls.BEHAVIOR]
        cls.tenant_id = cls.access_data.token.tenant.id_
        cls.addClassCleanup(cls.glance_behavior.resources.release)

        if cls.user_list.get('alt_user'):
            cls.alt_access_data = cls.user_list['alt_user'][cls.ACCESS_DATA]
            cls.alt_glance_client = cls.user_list['alt_user'][cls.CLIENT]
            cls.alt_glance_behavior = cls.user_list['alt_user'][cls.BEHAVIOR]
            cls.alt_tenant_id = cls.alt_access_data.token.tenant.id_
            cls.addClassCleanup(cls.alt_glance_behavior.resources.release)

        if cls.user_list.get('third_user'):
            cls.third_access_data = (
                cls.user_list['third_user'][cls.ACCESS_DATA])
            cls.third_glance_client = cls.user_list['third_user'][cls.CLIENT]
            cls.third_glance_behavior = (
                cls.user_list['third_user'][cls.BEHAVIOR])
            cls.third_tenant_id = cls.third_access_data.token.tenant.id_
            cls.addClassCleanup(cls.third_glance_behavior.resources.release)

        cls.status_code_msg = Messages.STATUS_CODE_MSG
        cls.id_regex = re.compile(ImageProperties.ID_REGEX)
        cls.import_from = cls.glance_config.import_from
        cls.import_from_bootable = cls.glance_config.import_from_bootable
        cls.import_from_format = cls.glance_config.import_from_format
        cls.export_to = cls.glance_config.export_to
        cls.max_created_at_delta = cls.glance_config.max_created_at_delta
        cls.max_expires_at_delta = cls.glance_config.max_expires_at_delta
        cls.max_updated_at_delta = cls.glance_config.max_updated_at_delta
        cls.test_file = cls.read_data_file(cls.glance_config.test_file)

        cls.addClassCleanup(cls.resources.release)

        cls.exception_handler = ExceptionHandler()
        cls.glance_client.add_exception_handler(cls.exception_handler)

    @classmethod
    def tearDownClass(cls):
        super(GlanceFixture, cls).tearDownClass()
        cls.resources.release()
        cls.glance_behavior.resources.release()
        if cls.user_list.get('alt_user'):
            cls.alt_glance_behavior.resources.release()
        if cls.user_list.get('third_user'):
            cls.third_glance_behavior.resources.release()
        cls.glance_client.delete_exception_handler(cls.exception_handler)

    @classmethod
    def generate_user_list(cls, account_list):
        """
        @summary: Generates list of users containing access_data, account
        types, behaviors, clients, and configurations
        """

        cls.ACCESS_DATA = "access_data"
        cls.BEHAVIOR = "behavior"
        cls.CLIENT = "client"
        cls.CONFIG = "config"
        user_list = dict()
        for user in account_list:
            user_list[user] = dict()
            user_list[user][cls.CONFIG] = UserConfig(section_name=user)
            user_list[user][cls.CONFIG].SECTION_NAME = user

            access_data = AuthProvider.get_access_data(
                cls.endpoint_config,
                user_config=user_list[user][cls.CONFIG])
            # If authentication fails, fail immediately
            if access_data is None:
                cls.assertClassSetupFailure('Authentication failed.')
            user_list[user][cls.ACCESS_DATA] = access_data

            glance_service = access_data.get_service(
                cls.glance_config.endpoint_name)
            glance_url_check = glance_service.get_endpoint(
                cls.glance_config.region)
            # If endpoint validation fails, fail immediately
            if glance_url_check is None:
                cls.assertClassSetupFailure('Endpoint validation failed')
            cls.url = (glance_service.get_endpoint(
                cls.glance_config.region).public_url)
            # If a url override was provided, use it instead
            if cls.glance_config.override_url:
                cls.url = cls.glance_config.override_url

            glance_client = cls.generate_glance_client(access_data)
            user_list[user][cls.CLIENT] = glance_client

            glance_behavior = GlanceBehaviors(glance_client, cls.glance_config)
            user_list[user][cls.BEHAVIOR] = glance_behavior

        return user_list

    @classmethod
    def generate_glance_client(cls, auth_data):
        """@summary: Returns new Glance client for requested auth data"""

        client_args = {'base_url': cls.url, 'auth_token': auth_data.token.id_,
                       'serialize_format': cls.serialize_format,
                       'deserialize_format': cls.deserialize_format}
        return GlanceClient(**client_args)

    @staticmethod
    def read_data_file(file_path):
        """@summary: Returns data file given a valid data file path"""
        try:
            with open(file_path, "r") as DATA:
                test_data = DATA.read().rstrip()
        except IOError as file_error:
            raise file_error

        return test_data

    @classmethod
    def get_comparison_data(cls, data_file):
        """
        @summary: Create comparison dictionary based on a given set of data
        """

        with open(data_file, "r") as DATA:
            all_data = DATA.readlines()

        comparison_dict = dict()
        for line in all_data:
            # Skip any comments or short lines
            if line.startswith('#') or len(line) < 5:
                continue
            # Get the defined data
            if line.startswith('+'):
                line = line.replace('+', '')
                data_columns = [x.strip().lower() for x in line.split('|')]
                continue
            # Process the data
            each_data = dict()
            data = [x.strip() for x in line.split("|")]
            for x, y in zip(data_columns[1:], data[1:]):
                each_data[x] = y
            comparison_dict[data[0]] = each_data

        return comparison_dict


class GlanceIntergrationFixture(ComputeFixture, ObjectStorageFixture):
    """
    @summary: Fixture for Compute API and Object Storage API integration
    with Glance
    """

    @classmethod
    def setUpClass(cls):
        super(GlanceIntergrationFixture, cls).setUpClass()
        cls.obj_storage_client = cls.client
