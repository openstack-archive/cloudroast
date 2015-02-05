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

from datetime import datetime

from cafe.drivers.unittest.datasets import DatasetList
from cloudcafe.common.tools.datagen import random_int, rand_name, random_string
from cloudcafe.glance.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageMemberStatus, ImageOSType,
    ImageStatus, ImageType, ImageVisibility, SortDirection)
from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


class ImagesDatasetListGenerator(object):
    """@summary: Generator for Images API"""

    @staticmethod
    def ListImagesFilters():
        """
        @summary: Generates a dataset list of filters for the list images
        request

        @return: Dataset_list
        @rtype: DatasetList
        """

        dataset_list = DatasetList()
        auto_disk_config = False
        checksum = random_string()
        container_format = ImageContainerFormat.AMI
        created_at = datetime.now()
        disk_format = ImageDiskFormat.RAW
        id_ = '8c178f37-2844-4ac4-b859-96047e585c3d'
        image_type = ImageType.IMPORT
        min_disk = images.config.min_disk
        min_ram = images.config.min_ram
        name = rand_name('image')
        os_type = ImageOSType.LINUX
        owner = random_int(0, 999999)
        protected = False
        size = random_int(0, 9999999)
        status = ImageStatus.ACTIVE
        updated_at = datetime.now()
        user_id = random_string()
        visibility = ImageVisibility.PUBLIC

        dataset_list.append_new_dataset(
            'passing_auto_disk_config',
            {'params': {'auto_disk_config': auto_disk_config}})
        dataset_list.append_new_dataset(
            'passing_checksum', {'params': {'checksum': checksum}})
        dataset_list.append_new_dataset(
            'passing_container_format',
            {'params': {'container_format': container_format}})
        dataset_list.append_new_dataset(
            'passing_created_at', {'params': {'created_at': created_at}})
        dataset_list.append_new_dataset(
            'passing_disk_format', {'params': {'disk_format': disk_format}})
        dataset_list.append_new_dataset('passing_id', {'params': {'id_': id_}})
        dataset_list.append_new_dataset(
            'passing_image_type', {'params': {'image_type': image_type}})
        dataset_list.append_new_dataset(
            'passing_min_disk', {'params': {'min_disk': min_disk}})
        dataset_list.append_new_dataset(
            'passing_min_ram', {'params': {'min_ram': min_ram}})
        dataset_list.append_new_dataset(
            'passing_multiple_filters',
            {'params': {'container_format': container_format,
                        'disk_format': disk_format}})
        dataset_list.append_new_dataset(
            'passing_name', {'params': {'name': name}})
        dataset_list.append_new_dataset(
            'passing_os_type', {'params': {'os_type': os_type}})
        dataset_list.append_new_dataset(
            'passing_owner', {'params': {'owner': owner}})
        dataset_list.append_new_dataset(
            'passing_protected', {'params': {'protected': protected}})
        dataset_list.append_new_dataset(
            'passing_size', {'params': {'size': size}})
        dataset_list.append_new_dataset(
            'passing_status', {'params': {'status': status}})
        dataset_list.append_new_dataset(
            'passing_updated_at', {'params': {'updated_at': updated_at}})
        dataset_list.append_new_dataset(
            'passing_user_id', {'params': {'user_id': user_id}})
        dataset_list.append_new_dataset(
            'passing_visibility', {'params': {'visibility': visibility}})

        return dataset_list

    @staticmethod
    def ListImagesParameters():
        """
        @summary: Generates a dataset list for the list images request
        containing parameters

        @return: Dataset_list
        @rtype: DatasetList
        """

        dataset_list = DatasetList()
        limit = 10
        marker = None
        sort_dir = SortDirection.ASCENDING
        sort_key = 'name'

        dataset_list.append_new_dataset(
            'passing_no_parameters', {'params': {}})
        dataset_list.append_new_dataset(
            'passing_limit', {'params': {'limit': limit}})
        dataset_list.append_new_dataset(
            'passing_marker', {'params': {'marker': marker}})
        dataset_list.append_new_dataset(
            'passing_sort_dir', {'params': {'sort_dir': sort_dir}})
        dataset_list.append_new_dataset(
            'passing_sort_key', {'params': {'sort_key': sort_key}})

        return dataset_list

    @staticmethod
    def ListImagesSort():
        """
        @summary: Generates a dataset list for the list images request
        containing sort options

        @return: Dataset_list
        @rtype: DatasetList
        """

        dataset_list = DatasetList()
        additional_prop = images.config.additional_property

        properties = [
            additional_prop, 'auto_disk_config', 'checksum',
            'container_format', 'created_at', 'disk_format', 'image_type',
            'min_disk', 'min_ram', 'name', 'os_type', 'owner', 'protected',
            'size', 'status', 'tags', 'updated_at', 'user_id', 'visibility']

        for prop in properties:
            dataset_list.append_new_dataset(
                'passing_sort_dir_asc_and_sort_key_{0}'.format(prop),
                {'params': {'sort_dir': SortDirection.ASCENDING,
                            'sort_key': prop}})
            dataset_list.append_new_dataset(
                'passing_sort_dir_desc_and_sort_key_{0}'.format(prop),
                {'params': {'sort_dir': SortDirection.DESCENDING,
                            'sort_key': prop}})

        return dataset_list

    @staticmethod
    def ListImagesInvalidParameters():
        """
        @summary: Generates a dataset list for the list images request
        containing invalid parameters

        @return: Dataset_list
        @rtype: DatasetList
        """

        dataset_list = DatasetList()

        dataset_list.append_new_dataset(
            'passing_invalid_limit', {'params': {'limit': 'invalid'}})
        dataset_list.append_new_dataset(
            'passing_invalid_marker', {'params': {'marker': 'invalid'}})
        dataset_list.append_new_dataset(
            'passing_invalid_sort_key', {'params': {'sort_key': 'invalid'}})
        dataset_list.append_new_dataset(
            'passing_invalid_sort_dir', {'params': {'sort_dir': 'invalid'}})

        return dataset_list

    @staticmethod
    def ListImageMembers():
        """
        @summary: Generates a dataset list for the list image members
        request

        @return: Dataset_list
        @rtype: DatasetList
        """

        dataset_list = DatasetList()

        member_status = ImageMemberStatus.ACCEPTED
        owner = random_int(0, 999999)
        visibility = ImageVisibility.PUBLIC

        dataset_list.append_new_dataset(
            'passing_no_parameters', {'params': {}})
        dataset_list.append_new_dataset(
            'passing_member_status',
            {'params': {'member_status': member_status}})
        dataset_list.append_new_dataset(
            'passing_owner', {'params': {'owner': owner}})
        dataset_list.append_new_dataset(
            'passing_visibility', {'params': {'visibility': visibility}})

        return dataset_list

    @staticmethod
    def Versions():
        """
        @summary: Generates a dataset list for the list versions request

        @return: Dataset_list
        @rtype: DatasetList
        """

        dataset_list = DatasetList()

        dataset_list.append_new_dataset(
            'url_with_no_backslash', {'url_addition': ''})
        dataset_list.append_new_dataset(
            'url_with_backslash', {'url_addition': '/'})
        dataset_list.append_new_dataset(
            'url_with_versions_and_no_backslash',
            {'url_addition': '/versions'})
        dataset_list.append_new_dataset(
            'url_with_versions_and_backslash', {'url_addition': '/versions/'})

        return dataset_list
