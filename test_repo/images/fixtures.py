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

import cStringIO as StringIO

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.images.config import ImagesConfig
from cloudcafe.auth.config import UserAuthConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.common.resources import ResourcePool
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.images.v1_0.client import ImagesClient as ImagesV1Client
from cloudcafe.images.v2_0.client import ImageClient as ImagesV2Client
from cloudcafe.images.behaviors import ImageBehaviors
from cloudcafe.images.common.types import ImageContainerFormat, ImageDiskFormat


class ImageFixture(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageFixture, cls).setUpClass()
        cls.config = ImagesConfig()
        cls.resources = ResourcePool()

    @classmethod
    def tearDownClass(cls):
        cls.resources.release()
        super(ImageFixture, cls).tearDownClass()


class ImageV1Fixture(ImageFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageV1Fixture, cls).setUpClass()
        access_data = AuthProvider().get_access_data()
        images_endpoint = '{base_url}/{api_version}'.format(
            base_url=cls.config.base_url,
            api_version=cls.config.api_version)

        cls.remote_image = cls.config.remote_image
        cls.http_image = cls.config.http_image

        cls.tenants_client = TenantsAPI_Client(UserAuthConfig().auth_endpoint,
                                               access_data.token.id_,
                                               'json', 'json')
        cls.tenants = cls._get_all_tenant_ids()

        cls.api_client = ImagesV1Client(images_endpoint, access_data.token.id_,
                                        'json', 'json')
        cls.behaviors = ImageBehaviors(cls.api_client, cls.config)

        if cls.__name__ == 'ListImagesTest':
            cls._setup_test_data()

    @classmethod
    def _setup_test_data(cls):  # setupClass doesn't run in fixture subclasses
        img1 = cls._create_remote_image('one', ImageContainerFormat.BARE,
                                        ImageDiskFormat.RAW)
        img2 = cls._create_remote_image('two', ImageContainerFormat.AMI,
                                        ImageDiskFormat.AMI)
        img3 = cls._create_remote_image('dup', ImageContainerFormat.BARE,
                                        ImageDiskFormat.RAW)
        img4 = cls._create_remote_image('dup', ImageContainerFormat.BARE,
                                        ImageDiskFormat.RAW)
        img5 = cls._create_standard_image('1', ImageContainerFormat.AMI,
                                          ImageDiskFormat.AMI, 42)
        img6 = cls._create_standard_image('2', ImageContainerFormat.AMI,
                                          ImageDiskFormat.AMI, 142)
        img7 = cls._create_standard_image('33', ImageContainerFormat.BARE,
                                          ImageDiskFormat.RAW, 142)
        img8 = cls._create_standard_image('33', ImageContainerFormat.BARE,
                                          ImageDiskFormat.RAW, 142)
        cls.created_images = set((img1, img2, img3, img4, img5, img6, img7,
                                  img8))
        cls.remote_set = set((img1, img2, img3, img4))
        cls.standard_set = set((img5, img6, img7, img8))
        cls.bare_set = set((img1, img3, img4, img7, img8))
        cls.ami_set = set((img2, img5, img6))
        cls.size42_set = set((img5,))
        cls.size142_set = set((img6, img7, img8))
        cls.dup_set = set((img3, img4))

        for img_id in cls.created_images:
            cls.resources.add(img_id, cls.api_client.delete_image)

    @classmethod
    def _create_remote_image(cls, name, container_format, disk_format):
        """
            Create new remote image.
            @return ID of the newly registered image
        """
        name = 'New Remote Image {0}'.format(name)

        response = cls.api_client.add_image(
            name,
            None,
            image_meta_container_format=container_format,
            image_meta_disk_format=disk_format,
            image_meta_is_public=True,
            image_meta_location=cls.remote_image)

        return response.entity.id

    @classmethod
    def _create_standard_image(cls, name, container_format, disk_format, size):
        """
            Create new standard image.
            @return ID of the newly registered image
        """
        image_data = StringIO.StringIO('*' * size)
        name = 'New Standard Image {0}'.format(name)

        response = cls.api_client.add_image(
            name,
            image_data,
            image_meta_container_format=container_format,
            image_meta_disk_format=disk_format,
            image_meta_is_public=True)

        return response.entity.id

    @classmethod
    def _get_all_tenant_ids(cls):
        """
            Get a list of all tenants
            @return list of Tenant IDs
        """
        response = cls.tenants_client.list_tenants()
        tenants = response.entity

        return [x.id_ for x in tenants]


class ImageV2Fixture(ImageFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageV2Fixture, cls).setUpClass()
        access_data = AuthProvider().get_access_data()
        images_endpoint = '{base_url}/{api_version}'.format(
            base_url=cls.config.base_url,
            api_version=cls.config.api_version)

        cls.api_client = ImagesV2Client(images_endpoint, access_data.token.id_,
                                        'json', 'json')
