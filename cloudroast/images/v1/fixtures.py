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

from cloudcafe.auth.config import UserAuthConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.images.v1_0.client import ImagesClient as ImagesV1Client
from cloudcafe.images.behaviors import ImageBehaviors

from cloudroast.images.fixtures import ImageFixture


class ImageV1Fixture(ImageFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageV1Fixture, cls).setUpClass()
        access_data = AuthProvider().get_access_data()
        images_endpoint = '{base_url}/v1'.format(
            base_url=cls.config.base_url)

        cls.remote_image = cls.config.remote_image
        cls.http_image = cls.config.http_image

        cls.tenants_client = TenantsAPI_Client(
            UserAuthConfig().auth_endpoint,
            access_data.token.id_,
            'json', 'json')
        cls.tenants = cls._get_all_tenant_ids()

        cls.api_client = ImagesV1Client(images_endpoint, access_data.token.id_,
                                        'json', 'json')
        cls.behaviors = ImageBehaviors(cls.api_client, cls.config)

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

        return response.entity.id_

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

        return response.entity.id_

    @classmethod
    def _get_all_tenant_ids(cls):
        """
            Get a list of all tenants
            @return list of Tenant IDs
        """
        response = cls.tenants_client.list_tenants()
        tenants = response.entity

        return [x.id_ for x in tenants]
