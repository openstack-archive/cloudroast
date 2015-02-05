"""
Copyright 2015 Rackspace

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
from cloudcafe.common.resources import ResourcePool
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.composite import (
    ImagesComposite, ImagesAuthComposite, ImagesAuthCompositeAltOne,
    ImagesAuthCompositeAltTwo)

from cloudroast.compute.fixtures import ComputeFixture
from cloudroast.objectstorage.fixtures import ObjectStorageFixture


class ImagesFixture(BaseTestFixture):
    """@summary: Fixture for Images API"""

    @classmethod
    def setUpClass(cls):
        super(ImagesFixture, cls).setUpClass()
        cls.resources = ResourcePool()

        user_one = ImagesAuthComposite()
        user_two = ImagesAuthCompositeAltOne()
        user_three = ImagesAuthCompositeAltTwo()

        cls.images = ImagesComposite(user_one)
        cls.images_alt_one = ImagesComposite(user_two)
        cls.images_alt_two = ImagesComposite(user_three)

        cls.status_code_msg = Messages.STATUS_CODE_MSG
        cls.ok_resp_msg = Messages.OK_RESP_MSG

        cls.addClassCleanup(cls.resources.release)

    @classmethod
    def get_comparison_data(cls, data_file):
        """
        @summary: Create comparison dictionary based on a given set of data

        @param data_file: File containing data to compare
        @param data_file: String
        @return: Comparison_dict
        @rtype: Dictionary
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


class ImagesIntergrationFixture(ComputeFixture, ImagesFixture,
                                ObjectStorageFixture):
    """
    @summary: Fixture for Compute API and Object Storage API integration
    with Images
    """

    @classmethod
    def setUpClass(cls):
        super(ImagesIntergrationFixture, cls).setUpClass()
        cls.obj_storage_client = cls.client
