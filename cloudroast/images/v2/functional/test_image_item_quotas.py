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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.images.fixtures import ImagesFixture


class TestImageItemQuotas(ImagesFixture):

    @unittest.skip('Bug, Redmine #3707')
    @tags(type='negative', regression='true')
    def test_add_image_member_quota_limit(self):
        """
        @summary: Add image members until quota limit is reached

        1) Create image
        2) Add image members until quota limit is reached
        3) Add one more image member
        4) Verify that the response code is 413
        5) Get image
        6) Verify that the response code is 200
        7) Verify that the number of image members matches the quota limit
        """

        self._validate_quota(
            api_name='add_member', items='members', success_resp=200,
            quota_limit=self.images_config.image_members_limit)

    @tags(type='negative', regression='true')
    def test_add_image_tag_quota_limit(self):
        """
        @summary: Add image tags until quota limit is reached

        1) Create image
        2) Add image tags until quota limit is reached
        3) Add one more image tag
        4) Verify that the response code is 413
        5) Get image
        6) Verify that the response code is 200
        7) Verify that the number of image tags matches the quota limit
        """

        self._validate_quota(
            api_name='add_tag', items='tags', success_resp=204,
            quota_limit=self.images_config.image_tags_limit)

    @tags(type='negative', regression='true')
    def test_update_image_property_quota_limit(self):
        """
        @summary: Update an image, adding image properties until quota limit is
        reached

        1) Create image
        2) Add image properties until quota limit is reached
        3) Add one more image property
        4) Verify that the response code is 413
        5) Get image
        6) Verify that the response code is 200
        7) Verify that the number of image properties matches the quota limit
        """

        quota_limit = self.images_config.image_properties_limit
        additional_props = ['auto_disk_config', 'image_type', 'os_type',
                            'user_id']

        image = self.images_behavior.create_image_via_task()
        # Subtract the properties that are added by default from the max limit
        for prop in additional_props:
            if hasattr(image, prop):
                quota_limit -= 1

        self._validate_quota(
            api_name='update_image', image=image,
            items='additional_properties', success_resp=200,
            quota_limit=quota_limit)

    def _validate_quota(self, api_name, items, success_resp, quota_limit,
                        image=None):
        """
        @summary: Given an a image item, validate that once a quota is reached,
        the expected error is returned
        @param api_name: The name of the api method
        @type name: String
        @param items: The items to be counted
        @type items: String
        @param success_resp: The expected success response code
        @type success_resp: Integer
        @param quota_limit: The maximum amount of items
        @type quota_limit: Integer
        @param image: The image object to be validated
        @type image: Image
        """

        if image is None:
            image = self.images_behavior.create_image_via_task()

        if api_name.lower() == 'add_member':
            response = self.images_client.list_members(image.id_)
            self.assertEqual(response.status_code, 200)
            members = response.entity
            number_of_items = len(members)
        else:
            number_of_items = len(getattr(image, items))
        api = getattr(self.images_client, api_name)

        while number_of_items != quota_limit:
            api_args = self._get_api_args(api_name, image)
            response = api(**api_args)
            self.assertEqual(response.status_code, success_resp)
            if api_name.lower() == 'add_member':
                response = self.images_client.list_members(image.id_)
                self.assertEqual(response.status_code, 200)
                members = response.entity
                number_of_items = len(members)
            else:
                response = self.images_client.get_image(image.id_)
                self.assertEqual(response.status_code, 200)
                image = response.entity
                number_of_items = len(getattr(image, items))

        api_args = self._get_api_args(api_name, image)
        response = api(**api_args)
        self.assertEqual(response.status_code, 413)

        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(len(getattr(get_image, items)), quota_limit)

    def _get_api_args(self, api_name, image):
        """
        @summary: Given an a api_name, return the proper api_args
        @param api_name: The name of the api method
        @type name: String
        @param image: The image object to be validated
        @type image: Image
        @return: The arguments to be passed to an api call
        @rtype: Dictionary
        """

        if api_name.lower() == 'add_member':
            api_args = dict(image_id=image.id_, member_id=rand_name('member'))
        elif api_name.lower() == 'add_tag':
            api_args = dict(image_id=image.id_, tag=rand_name('tag'))
        else:
            api_args = dict(image_id=image.id_,
                            add={rand_name('prop'): rand_name('prop_value')})

        return api_args
