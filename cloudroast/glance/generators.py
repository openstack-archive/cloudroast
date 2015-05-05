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
import uuid

from cafe.drivers.unittest.datasets import DatasetList
from cloudcafe.common.tools.datagen import random_int, rand_name, random_string
from cloudcafe.glance.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageMemberStatus, ImageOSType,
    ImageStatus, ImageType, ImageVisibility, Schemas, SortDirection)
from cloudcafe.glance.composite import (
    ImagesComposite, ImagesAuthComposite, ImagesAuthCompositeAdmin)

user_one = ImagesAuthComposite()
user_admin = ImagesAuthCompositeAdmin()
images = ImagesComposite(user_one)
images_admin = ImagesComposite(user_admin)


class ImagesDatasetListGenerator(object):
    """@summary: Generators for Images API"""

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
        id_ = str(uuid.uuid1())
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

        data_dict = {'passing_limit': {'limit': limit},
                     'passing_marker': {'marker': marker},
                     'passing_sort_dir': {'sort_dir': sort_dir},
                     'passing_sort_key': {'sort_key': sort_key}}

        return build_basic_dataset(data_dict, 'params')

    @staticmethod
    def ListImagesSmoke():
        """
        @summary: Generates a dataset list of parameters for the list images
        request for smoke tests

        @return: Dataset_list
        @rtype: DatasetList
        """

        additional_property = images.config.additional_property
        additional_property_value = images.config.additional_property_value
        auto_disk_config = 'False'
        checksum = random_string()
        container_format = ImageContainerFormat.AMI
        created_at = datetime.now()
        disk_format = ImageDiskFormat.RAW
        id_ = str(uuid.uuid1())
        image_type = ImageType.IMPORT
        limit = 10
        marker = None
        member_status = ImageMemberStatus.ACCEPTED
        min_disk = images.config.min_disk
        min_ram = images.config.min_ram
        name = rand_name('image')
        os_type = ImageOSType.LINUX
        owner = random_int(0, 999999)
        protected = False
        size = random_int(0, 9999999)
        size_max = images.config.size_max
        size_min = images.config.size_min
        status = ImageStatus.ACTIVE
        sort_dir = SortDirection.ASCENDING
        sort_key = 'name'
        tag = [rand_name('tag')]
        updated_at = datetime.now()
        user_id = random_string()
        visibility = ImageVisibility.SHARED

        data_dict = {'passing_additional_property':
                     {additional_property: additional_property_value},
                     'passing_auto_disk_config':
                     {'auto_disk_config': auto_disk_config},
                     'passing_checksum': {'checksum': checksum},
                     'passing_container_format':
                     {'container_format': container_format},
                     'passing_created_at': {'created_at': created_at},
                     'passing_disk_format': {'disk_format': disk_format},
                     'passing_id': {'id_': id_},
                     'passing_image_type': {'image_type': image_type},
                     'passing_limit': {'limit': limit},
                     'passing_marker': {'marker': marker},
                     'passing_member_status': {'member_status': member_status,
                                               'visibility': visibility},
                     'passing_min_disk': {'min_disk': min_disk},
                     'passing_min_ram': {'min_ram': min_ram},
                     'passing_name': {'name': name},
                     'passing_no_parameters': {},
                     'passing_os_type': {'os_type': os_type},
                     'passing_owner': {'owner': owner},
                     'passing_protected': {'protected': protected},
                     'passing_size': {'size': size},
                     'passing_size_max': {'size_max': size_max},
                     'passing_size_min': {'size_min': size_min},
                     'passing_sort_dir': {'sort_dir': sort_dir},
                     'passing_sort_key': {'sort_key': sort_key},
                     'passing_status': {'status': status},
                     'passing_tag': {'tag': tag},
                     'passing_updated_at': {'updated_at': updated_at},
                     'passing_user_id': {'user_id': user_id},
                     'passing_visibility': {'visibility': visibility}}

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

        properties = [
            'container_format', 'created_at', 'disk_format', 'id', 'name',
            'size', 'status', 'updated_at']

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

        additional_property = images.config.additional_property

        data_dict = {'passing_additional_property':
                     {additional_property: 'invalid'},
                     'passing_auto_disk_config':
                     {'auto_disk_config': 'invalid'},
                     'passing_checksum': {'checksum': 'invalid'},
                     'passing_container_format':
                     {'container_format': 'invalid'},
                     'passing_created_at': {'created_at': 'invalid'},
                     'passing_disk_format': {'disk_format': 'invalid'},
                     'passing_id': {'id': 'invalid'},
                     'passing_image_type': {'image_type': 'invalid'},
                     'passing_invalid_limit': {'limit': 'invalid'},
                     'passing_marker': {'marker': 'invalid'},
                     'passing_member_status': {'member_status': 'invalid',
                                               'visibility': 'invalid'},
                     'passing_min_disk': {'min_disk': 'invalid'},
                     'passing_min_ram': {'min_ram': 'invalid'},
                     'passing_name': {'name': 'invalid'},
                     'passing_os_type': {'os_type': 'invalid'},
                     'passing_owner': {'owner': 'invalid'},
                     'passing_protected': {'protected': 'invalid'},
                     'passing_size': {'size': 'invalid'},
                     'passing_size_max': {'size_max': 'invalid'},
                     'passing_size_min': {'size_min': 'invalid'},
                     'passing_sort_dir': {'sort_dir': 'invalid'},
                     'passing_sort_key': {'sort_key': 'invalid'},
                     'passing_status': {'status': 'invalid'},
                     'passing_tag': {'tag': 'invalid'},
                     'passing_updated_at': {'updated_at': 'invalid'},
                     'passing_user_id': {'user_id': 'invalid'},
                     'passing_visibility': {'visibility': 'invalid'}}

        return build_basic_dataset(data_dict, 'prop')

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
        protected = False
        tags = [rand_name('tag1')]

        data_dict = {
            'passing_auto_disk_config': {'auto_disk_config': auto_disk_config},
            'passing_min_disk': {'min_disk': min_disk},
            'passing_min_ram': {'min_ram': min_ram},
            'passing_name': {'name': name},
            'passing_protected': {'protected': protected},
            'passing_tags': {'tags': tags}}

        if image_status == ImageStatus.QUEUED:
            data_dict.update({'passing_container_format':
                              {'container_format': container_format},
                              'passing_disk_format':
                              {'disk_format': disk_format}})
            data_dict.pop('passing_auto_disk_config')

        return build_basic_dataset(data_dict, 'prop')

    @staticmethod
    def UpdateImageInaccessible():
        """
        @summary: Generates a dataset list of properties that are inaccessible
        to the user for the update image request

        @return: Dataset_list
        @rtype: DatasetList
        """

        image_id = str(uuid.uuid1())

        deleted = True
        deleted_at = str(datetime.now())
        location = '/v2/images/{0}/test_file'.format(image_id)
        virtual_size = images.config.size_default

        data_dict = {
            'passing_deleted': {'deleted': deleted},
            'passing_deleted_at': {'deleted_at': deleted_at},
            'passing_location': {'location': location},
            'passing_virtual_size': {'virtual_size': virtual_size}}

        return build_basic_dataset(data_dict, 'prop')

    @staticmethod
    def UpdateAddRemoveImageRestricted():
        """
        @summary: Generates a dataset list of properties that are restricted
        for the update and register image requests

        @return: Dataset_list
        @rtype: DatasetList
        """

        image_id = str(uuid.uuid1())

        # Properties that are read-only
        checksum = random_string()
        created_at = str(datetime.now())
        file_ = '/v2/images/{0}/file'.format(image_id)
        id_ = str(uuid.uuid1())
        schema = Schemas.IMAGE_MEMBER_SCHEMA
        self_ = '/v2/images/{0}'.format(image_id)
        size = random_int(0, 9999999)
        status = ImageStatus.ACTIVE
        updated_at = str(datetime.now())

        # Properties that are reserved
        image_type = ImageType.IMPORT
        location = '/v2/images/{0}/file'.format(image_id)
        os_type = ImageOSType.LINUX
        owner = str(random_int(0, 999999))
        user_id = random_string()

        # Properties that unauthorized
        visibility = ImageVisibility.PRIVATE

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
            'passing_location': {'location': location},
            'passing_os_type': {'os_type': os_type},
            'passing_owner': {'owner': owner},
            'passing_user_id': {'user_id': user_id},
            'passing_visibility': {'visibility': visibility}}

        return build_basic_dataset(data_dict, 'prop')

    @staticmethod
    def UpdateReplaceImageRestricted():
        """
        @summary: Generates a dataset list of properties that are restricted
        for the update and register image requests

        @return: Dataset_list
        @rtype: DatasetList
        """

        image_id = str(uuid.uuid1())

        # Properties that are read-only
        checksum = random_string()
        created_at = str(datetime.now())
        file_ = '/v2/images/{0}/file'.format(image_id)
        id_ = str(uuid.uuid1())
        schema = Schemas.IMAGE_MEMBER_SCHEMA
        self_ = '/v2/images/{0}'.format(image_id)
        size = random_int(0, 9999999)
        status = ImageStatus.ACTIVE
        updated_at = str(datetime.now())

        # Properties that are reserved
        image_type = ImageType.IMPORT
        location = '/v2/images/{0}/file'.format(image_id)
        os_type = ImageOSType.LINUX
        owner = str(random_int(0, 999999))
        user_id = random_string()

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
            'passing_location': {'location': location},
            'passing_os_type': {'os_type': os_type},
            'passing_owner': {'owner': owner},
            'passing_user_id': {'user_id': user_id}}

        return build_basic_dataset(data_dict, 'prop')

    @staticmethod
    def RegisterImageRestricted():
        """
        @summary: Generates a dataset list of properties that are restricted
        for the register image request

        @return: Dataset_list
        @rtype: DatasetList
        """

        image_id = str(uuid.uuid1())

        # Properties that are read-only
        checksum = random_string()
        created_at = str(datetime.now())
        file_ = '/v2/images/{0}/file'.format(image_id)
        schema = Schemas.IMAGE_MEMBER_SCHEMA
        self_ = '/v2/images/{0}'.format(image_id)
        size = random_int(0, 9999999)
        status = ImageStatus.ACTIVE
        updated_at = str(datetime.now())

        # Properties that are reserved
        owner = str(random_int(0, 999999))

        data_dict = {
            'passing_checksum': {'checksum': checksum},
            'passing_created_at': {'created_at': created_at},
            'passing_file': {'file': file_},
            'passing_schema': {'schema': schema},
            'passing_self': {'self': self_}, 'passing_size': {'size': size},
            'passing_status': {'status': status},
            'passing_updated_at': {'updated_at': updated_at},
            'passing_owner': {'owner': owner}}

        return build_basic_dataset(data_dict, 'prop')

    @staticmethod
    def RegisterImageInvalidValues():
        """
        @summary: Generates a dataset list of properties that are invalid
        values for the register image request

        @return: Dataset_list
        @rtype: DatasetList
        """

        container_format = 'invalid'
        disk_format = 'invalid'
        min_disk = 'invalid'
        min_ram = 'invalid'
        name = 0
        protected = 'invalid'
        tags = 0

        data_dict = {
            'passing_invalid_container_format':
            {'container_format': container_format},
            'passing_invalid_disk_format': {'disk_format': disk_format},
            'passing_invalid_min_disk': {'min_disk': min_disk},
            'passing_invalid_min_ram': {'min_ram': min_ram},
            'passing_invalid_name': {'name': name},
            'passing_invalid_protected': {'protected': protected},
            'passing_invalid_tags': {'tags': tags}}

        return build_basic_dataset(data_dict, 'prop')

    @staticmethod
    def DeactivateImages():
        """
        @summary: Generates a dataset list of images for the deactivate image
        request

        @return: Dataset_list
        @rtype: DatasetList
        """

        created_images = images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('deactivate_image')}, count=3)

        private_image = created_images.pop()

        deactivated_image = created_images.pop()
        images_admin.client.deactivate_image(deactivated_image.id_)

        public_image = created_images.pop()
        images_admin.client.update_image(
            public_image.id_, replace={'visibility': ImageVisibility.PUBLIC})

        data_dict = {
            'passing_deactivated_image': deactivated_image,
            'passing_private_image': private_image,
            'passing_public_image': public_image}

        return build_basic_dataset(data_dict, 'image')

    @staticmethod
    def ReactivateImages():
        """
        @summary: Generates a dataset list of images for the reactivate image
        request

        @return: Dataset_list
        @rtype: DatasetList
        """

        created_images = images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('reactivate_image')}, count=4)

        active_image = created_images.pop()

        private_image = created_images.pop()
        images_admin.client.deactivate_image(private_image.id_)

        reactivated_image = created_images.pop()
        images_admin.client.deactivate_image(reactivated_image.id_)
        images_admin.client.reactivate_image(reactivated_image.id_)

        public_image = created_images.pop()
        images_admin.client.update_image(
            public_image.id_, replace={'visibility': ImageVisibility.PUBLIC})
        images_admin.client.reactivate_image(public_image.id_)

        data_dict = {
            'passing_active_image': active_image,
            'passing_private_image': private_image,
            'passing_public_image': public_image,
            'passing_reactivated_image': reactivated_image}

        return build_basic_dataset(data_dict, 'image')

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
