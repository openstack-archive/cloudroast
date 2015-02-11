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
    ImageStatus, ImageType, ImageVisibility, Schemas, SortDirection)
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

        auto_disk_config = 'False'
        checksum = random_string()
        container_format = ImageContainerFormat.AMI
        created_at = datetime.now()
        disk_format = ImageDiskFormat.RAW
        id_ = '00000000-0000-0000-0000-000000000000'
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

        data_dict = {'passing_auto_disk_config':
                     {'auto_disk_config': auto_disk_config},
                     'passing_checksum': {'checksum': checksum},
                     'passing_container_format':
                     {'container_format': container_format},
                     'passing_created_at': {'created_at': created_at},
                     'passing_disk_format': {'disk_format': disk_format},
                     'passing_id': {'id_': id_},
                     'passing_image_type': {'image_type': image_type},
                     'passing_min_disk': {'min_disk': min_disk},
                     'passing_min_ram': {'min_ram': min_ram},
                     'passing_multiple_filters':
                     {'container_format': container_format,
                      'disk_format': disk_format},
                     'passing_name': {'name': name},
                     'passing_os_type': {'os_type': os_type},
                     'passing_owner': {'owner': owner},
                     'passing_protected': {'protected': protected},
                     'passing_size': {'size': size},
                     'passing_status': {'status': status},
                     'passing_updated_at': {'updated_at': updated_at},
                     'passing_user_id': {'user_id': user_id},
                     'passing_visibility': {'visibility': visibility}}

        return build_basic_dataset(data_dict, 'params')

    @staticmethod
    def ListImagesParameters():
        """
        @summary: Generates a dataset list of parameters for the list images
        request

        @return: Dataset_list
        @rtype: DatasetList
        """

        limit = 10
        marker = None
        sort_dir = SortDirection.ASCENDING
        sort_key = 'name'

        data_dict = {'passing_no_parameters': {},
                     'passing_limit': {'limit': limit},
                     'passing_marker': {'marker': marker},
                     'passing_sort_dir': {'sort_dir': sort_dir},
                     'passing_sort_key': {'sort_key': sort_key}}

        return build_basic_dataset(data_dict, 'params')

    @staticmethod
    def ListImagesSort():
        """
        @summary: Generates a dataset list of sort parameters for the list
        images request

        @return: Dataset_list
        @rtype: DatasetList
        """

        data_dict = {}
        additional_prop = images.config.additional_property

        properties = [
            additional_prop, 'auto_disk_config', 'checksum',
            'container_format', 'created_at', 'disk_format', 'image_type',
            'min_disk', 'min_ram', 'name', 'os_type', 'owner', 'protected',
            'size', 'status', 'tags', 'updated_at', 'user_id', 'visibility']

        for prop in properties:
            data_dict.update(
                {'passing_sort_dir_asc_and_sort_key_{0}'.format(prop):
                 {'sort_dir': SortDirection.ASCENDING, 'sort_key': prop}})
            data_dict.update(
                {'passing_sort_dir_desc_and_sort_key_{0}'.format(prop):
                 {'sort_dir': SortDirection.DESCENDING, 'sort_key': prop}})

        return build_basic_dataset(data_dict, 'params')

    @staticmethod
    def ListImagesInvalidParameters():
        """
        @summary: Generates a dataset list of invalid parameters for the list
        images request

        @return: Dataset_list
        @rtype: DatasetList
        """

        data_dict = {'passing_invalid_limit': {'limit': 'invalid'},
                     'passing_invalid_marker': {'marker': 'invalid'},
                     'passing_invalid_sort_key': {'sort_key': 'invalid'},
                     'passing_invalid_sort_dir': {'sort_dir': 'invalid'}}

        return build_basic_dataset(data_dict, 'property')

    @staticmethod
    def UpdateImageAllowed(image_status=ImageStatus.ACTIVE):
        """
        @summary: Generates a dataset list of properties that are allowed to be
        updated for the update image request

        @param image_status: Status of image being updated
        @type image_status: String

        @return: Dataset_list
        @rtype: DatasetList
        """

        auto_disk_config = 'False'
        container_format = ImageContainerFormat.AKI
        disk_format = ImageDiskFormat.ISO
        min_disk = images.config.min_disk
        min_ram = images.config.min_ram
        name = rand_name('image')
        tags = [rand_name('tag1')]
        protected = False

        data_dict = {
            'passing_auto_disk_config': {'auto_disk_config': auto_disk_config},
            'passing_min_disk': {'min_disk': min_disk},
            'passing_min_ram': {'min_ram': min_ram},
            'passing_name': {'name': name}, 'passing_tags': {'tags': tags},
            'passing_protected': {'protected': protected}}

        if image_status == ImageStatus.QUEUED:
            data_dict.update({'passing_container_format':
                              {'container_format': container_format},
                              'passing_disk_format':
                              {'disk_format': disk_format}})
            data_dict.pop('passing_auto_disk_config')

        return build_basic_dataset(data_dict, 'property')

    @staticmethod
    def UpdateImageInaccessible():
        """
        @summary: Generates a dataset list of properties that are inaccessible
        to the user for the update image request

        @return: Dataset_list
        @rtype: DatasetList
        """

        deleted = True
        deleted_at = str(datetime.now())
        location = '/v2/images/00000000-0000-0000-0000-000000000000/test_file'
        virtual_size = images.config.size_default

        data_dict = {
            'passing_deleted': {'deleted': deleted},
            'passing_deleted_at': {'deleted_at': deleted_at},
            'passing_location': {'location': location},
            'passing_virtual_size': {'virtual_size': virtual_size}}

        return build_basic_dataset(data_dict, 'property')

    @staticmethod
    def UpdateImageRestricted():
        """
        @summary: Generates a dataset list of properties that are restricted
        for the update image request

        @return: Dataset_list
        @rtype: DatasetList
        """

        # Properties that are read-only
        id_ = '00000000-0000-0000-0000-000000000000'
        checksum = random_string()
        created_at = str(datetime.now())
        file_ = '/v2/images/00000000-0000-0000-0000-000000000000/file'
        schema = Schemas.IMAGE_MEMBER_SCHEMA
        self_ = '/v2/images/00000000-0000-0000-0000-000000000000'
        size = random_int(0, 9999999)
        status = ImageStatus.ACTIVE
        updated_at = str(datetime.now())

        # Properties that are reserved
        image_type = ImageType.IMPORT
        os_type = ImageOSType.LINUX
        owner = random_int(0, 999999)
        user_id = random_string()

        # Properties that unauthorized
        visibility = ImageVisibility.PUBLIC

        data_dict = {
            'passing_id': {'id': id_},
            'passing_checksum': {'checksum': checksum},
            'passing_created_at': {'created_at': created_at},
            'passing_file': {'file': file_},
            'passing_schema': {'schema': schema},
            'passing_self': {'self': self_}, 'passing_size': {'size': size},
            'passing_status': {'status': status},
            'passing_updated_at': {'updated_at': updated_at},
            'passing_image_type': {'image_type': image_type},
            'passing_os_type': {'os_type': os_type},
            'passing_owner': {'owner': owner},
            'passing_user_id': {'user_id': user_id},
            'passing_visibility': {'visibility': visibility}}

        return build_basic_dataset(data_dict, 'property')

    @staticmethod
    def ListImageMembers():
        """
        @summary: Generates a dataset list of parameters for the list image
        members request

        @return: Dataset_list
        @rtype: DatasetList
        """

        member_status = ImageMemberStatus.ACCEPTED
        owner = random_int(0, 999999)
        visibility = ImageVisibility.PUBLIC

        data_dict = {'passing_no_parameters': {},
                     'passing_member_status': {'member_status': member_status},
                     'passing_owner': {'owner': owner},
                     'passing_visibility': {'visibility': visibility}}

        return build_basic_dataset(data_dict, 'params')

    @staticmethod
    def Versions():
        """
        @summary: Generates a dataset list of url additions for the list
        versions request

        @return: Dataset_list
        @rtype: DatasetList
        """

        data_dict = {'url_with_no_backslash': '', 'url_with_backslash': '/',
                     'url_with_versions_and_no_backslash': '/versions',
                     'url_with_versions_and_backslash': '/versions/'}

        return build_basic_dataset(data_dict, 'url_addition')


def build_basic_dataset(data_dict, name):
    """
    @summary: Builds a dataset list from a dictionary of key-value pairs

    @param data_dict: Url amendments and values for the dataset list
    @type data_dict: Dictionary
    @param name: Name of the test parameter
    @type name: String

    @return: Dataset_List
    @rtype: DatasetList
    """

    dataset_list = DatasetList()

    for key, value in data_dict.iteritems():
        dataset_list.append_new_dataset(key, {name: value})

    return dataset_list
