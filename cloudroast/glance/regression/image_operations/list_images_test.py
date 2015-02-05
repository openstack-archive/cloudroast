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

import sys
import unittest

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.types import (
    ImageStatus, ImageVisibility, SortDirection)

from cloudroast.glance.fixtures import ImagesIntergrationFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class ListImages(ImagesIntergrationFixture):

    @classmethod
    def setUpClass(cls):
        super(ListImages, cls).setUpClass()

        member_id = cls.images_alt_one.auth.tenant_id

        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('image')})
        cls.created_image = created_images.pop()

        cls.images.client.create_image_member(
            cls.created_image.id_, member_id)
        resp = cls.images.client.get_image_member(
            cls.created_image.id_, member_id)
        cls.created_image_member = resp.entity

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ListImages, cls).tearDownClass()

    def test_compare_list_images_between_glance_and_nova(self):
        """
        @summary: Compare the list of images returned from the glance api and
        the nova api

        1) List images with a limit set to 100 and visiblity set to public
        through the glance api
        2) Verify that the response is ok
        3) Verify that the images returned is not none
        4) List images with a limit set to 100 and image_type set to base
        through the nova api
        5) Verify that the response is ok
        6) Verify that the images returned is not none
        7) Verify that the length of the list of images is the same through the
        glance api and the nova api
        8) Verify that each image name in the list of images is the same
        through the glance api and the nova api
        """

        resp = self.images.client.list_images(
            params={'limit': 100, 'visibility': ImageVisibility.PUBLIC})
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        glance_image_names = [image.name for image in resp.entity]
        self.assertIsNotNone(
            glance_image_names, msg=('Unexpected images received.'
                                     'Expected: At least one image received '
                                     'Received: No images received'))

        resp = self.compute.images.client.list_images_with_detail(
            limit=100, image_type='base')
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        nova_image_names = [image.name for image in resp.entity]
        self.assertIsNotNone(
            nova_image_names, msg=('Unexpected images received.'
                                   'Expected: At least one image received '
                                   'Received: No images received'))

        self.assertEqual(
            len(glance_image_names), len(nova_image_names),
            msg=('Unexpected images received. Expected: Number of images to '
                 'match Received: Number of images do not match'))

        for image_name in glance_image_names:
            self.assertIn(
                image_name, nova_image_names,
                msg=('Unexpected images received. Expected: {0} in list of '
                     'images '
                     'Received: {1}').format(image_name, nova_image_names))

    def test_list_all_images(self):
        """
        @summary: List all images with no additional query parameters,
        paginating through the results as needed, and verify that the created
        image is listed

        1) List all images not passing in any additional query parameter,
        paginating through the results as needed
        2) Verify that the list is not empty
        3) Verify that the created image is in the returned list of images
        4) Verify that each image returned has a status of active
        """

        listed_images = self.images.behaviors.list_all_images()
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        self.assertIn(
            self.created_image, listed_images,
            msg=('Unexpected images received. Expected: {0} in list of '
                 'images '
                 'Received: {1}').format(self.created_image, listed_images))

        # TODO: Add additional assertions to verify all images are as expected
        for image in listed_images:
            self.assertEqual(
                image.status, ImageStatus.ACTIVE,
                msg=('Unexpected status for image {0} received. Expected: {1} '
                     'Received: {2}').format(image.id_,
                                             ImageStatus.ACTIVE, image.status))

    @data_driven_test(
        ImagesDatasetListGenerator.ListImagesFilters())
    def ddtest_filter_images_list(self, params):
        """
        @summary: List all images that match a filter, passing in a specific
        query parameter

        @param param: Parameter being passed to the list images request
        @type param: Dictionary

        1) List all images passing in a query parameter
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for the given
        filter that is acceptable
        """

        # This is a temporary workaround for skips in ddtests
        if 'id_' in params or 'created_at' in params:
            sys.stderr.write('skipped \'Redmine bug #11168\' ... ')
            return

        api_args = {}

        for param in params:
            api_args.update({param: getattr(self.created_image, param)})

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not 0 '
                 'Received: {0}').format(len(listed_images)))

        for image in listed_images:
            for param in params:
                received = getattr(image, param)
                expected = getattr(self.created_image, param)
                self.assertEqual(
                    received, expected,
                    msg=('Unexpected property value for image {0} received.'
                         'Expected: {1} '
                         'Received: {2}').format(image.id_, expected,
                                                 received))

    def test_filter_images_list_passing_additional_property(self):
        """
        @summary: List all images that match a filter, passing in an additional
        property as the query parameter

        1) List all images passing in an additional property as the query
        parameter
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for the additional
        property that matches the additional property that is being used as the
        filter
        """

        prop = self.images.config.additional_property

        api_args = ({prop: self.created_image.additional_properties.get(prop)})

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not 0 '
                 'Received: {0}').format(len(listed_images)))

        for image in listed_images:
            received = image.additional_properties.get(prop)
            expected = (self.created_image.additional_properties.get(prop))
            self.assertEqual(
                received, expected,
                msg=('Unexpected property for image {0} received.'
                     'Expected: {1} '
                     'Received: {2}').format(image.id_, expected, received))

    @unittest.skip('Redmine bug #11270')
    def test_filter_images_list_passing_member_status(self):
        """
        @summary: List all images that match a filter, passing in member_status
        as the query parameter

        1) List all images passing in member_status as the query parameter
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned list image members
        4) Verify that each image returned contains a value for member_status
        that matches the member_status that is being used as the filter
        """

        api_args = ({'member_status':
                     getattr(self.created_image_member, 'status'),
                     'visibility': getattr(self.created_image, 'visibility')})

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for image in listed_images:
            image_member_statuses = []
            resp = self.images.client.list_image_members(image.id_)
            self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
            list_image_members = resp.entity
            for member in list_image_members:
                image_member_statuses.append(member.status)
                received_image_member_status = (
                    getattr(self.created_image_member, 'status'))
                self.assertIn(getattr(self.created_image_member, 'status'),
                              image_member_statuses,
                              msg=('Unexpected image member status for image'
                                   '{0} received. Expected: {1} in list of'
                                   'image member statuses Received: '
                                   '{2}').format(image.id_,
                                                 received_image_member_status,
                                                 image_member_statuses))

    def test_filter_images_list_passing_size_max(self):
        """
        @summary: List all images that match a filter, passing in size_max as
        the query parameter

        1) List all images passing in size_max as the query parameter
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for size that is
        less than or equal to the size_max that is being used as the filter
        """

        api_args = {'size_max': self.images.config.size_max}

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for image in listed_images:
            received = getattr(image, 'size')
            expected = self.images.config.size_max
            self.assertLessEqual(
                received, expected,
                msg=('Unexpected size_max for image {0} received.'
                     'Expected: <= {1} '
                     'Received: {2}').format(image.id_, expected, received))

    def test_filter_images_list_passing_size_max_and_size_min(self):
        """
        @summary: List all images that match a filter, passing in both size_max
        and size_min as the query parameters

        1) List all images passing in size_max and size_min as the query
        parameters
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for size that is
        less than or equal to the size_max that is being used as the filter and
        greater than or equal to the size_min that is being used as the filter
        """

        api_args = {'size_max': self.images.config.size_max,
                    'size_min': self.images.config.size_min}

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for image in listed_images:
            received = getattr(image, 'size')
            expected = self.images.config.size_max
            self.assertLessEqual(
                received, expected,
                msg=('Unexpected size_max for image {0} received.'
                     'Expected: <= {1} '
                     'Received: {2}').format(image.id_, expected, received))
            expected = getattr(self.images.config, 'size_min')
            self.assertGreaterEqual(
                received, expected,
                msg=('Unexpected size_min for image {0} received.'
                     'Expected: >= {1} '
                     'Received: {2}').format(image.id_, expected, received))

    def test_filter_images_list_passing_size_min(self):
        """
        @summary: List all images that match a filter, passing in size_min as
        the query parameter

        1) List all images passing in size_min as the query parameter
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for size that is
        greater than or equal to the size_min that is being used as the filter
        """

        api_args = {'size_min': self.images.config.size_min}

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for image in listed_images:
            received = getattr(image, 'size')
            expected = self.images.config.size_min
            self.assertGreaterEqual(
                received, expected,
                msg=('Unexpected size_min for image {0} received.'
                     'Expected: >= {1} '
                     'Received: {2}').format(image.id_, expected, received))

    def test_filter_images_list_passing_tag(self):
        """
        @summary: List all images that match a filter, passing in tag as
        the query parameter

        1) List all images passing in tag as the query parameter
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for tags that
        matches the tag that is being used as the filter
        """

        api_args = {'tag': getattr(self.created_image, 'tags')}

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for image in listed_images:
            received = getattr(image, 'tags')
            expected = getattr(self.created_image, 'tags')
            self.assertEqual(
                received, expected,
                msg=('Unexpected tags for image {0} received. Expected: {1} '
                     'Received: {2}').format(image.id_, expected, received))

    def test_list_images_using_limit(self):
        """
        @summary: List images using limit

        1) List images passing in 1 as the limit
        2) Verify that the response code is ok
        4) Verify that the number of images returned is 1
        """

        resp = self.images.client.list_images(params={'limit': 1})
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_images = resp.entity
        self.assertEqual(
            len(listed_images), 1,
            msg=('Unexpected number of images received. Expected: {0} '
                 'Received: {1}').format(1, len(listed_images)))

    def test_list_images_using_limit_zero(self):
        """
        @summary: List images using limit of zero

        1) List images passing in 0 as the limit
        2) Verify that the response code is ok
        3) Verify that the number of images returned is 0
        """

        resp = self.images.client.list_images(params={'limit': 0})
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_images = resp.entity
        self.assertEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: {0} '
                 'Received: {1}').format(0, len(listed_images)))

    def test_list_images_using_marker_pagination(self):
        """
        @summary: List images using marker pagination

        1) List images passing in 1 as the limit, the created image's name as
        the name, and the user as the owner
        2) Verify that the response code is ok
        3) Verify that the returned list only contains 1 image
        4) List images again passing in the listed image id as the marker as
        well as 1 as the limit, the created image's name as the name, and the
        user as the owner
        5) Verify that the response code is ok
        6) Verify that the returned list only contains 1 image
        7) Verify that the newly returned image is not the same as the
        previously returned image
        """

        resp = self.images.client.list_images(
            params={'limit': 1, 'name': self.created_image.name,
                    'owner': self.images.auth.tenant_id})
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_image = resp.entity
        self.assertEqual(
            len(listed_image), 1,
            msg=('Unexpected number of images received. Expected: {0} '
                 'Received: {1}').format(1, len(listed_image)))

        marker = listed_image[0].id_

        resp = self.images.client.list_images(
            params={'limit': 1, 'marker': marker,
                    'name': self.created_image.name,
                    'owner': self.images.auth.tenant_id})
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        next_listed_image = resp.entity
        self.assertEqual(
            len(next_listed_image), 1,
            msg=('Unexpected number of images received. Expected: {0} '
                 'Received: {1}').format(1, len(next_listed_image)))

        self.assertNotEqual(
            listed_image[0], next_listed_image[0],
            msg=('Unexpected images received. Expected: Images to not match '
                 'Received: Images match'))

    @data_driven_test(
        ImagesDatasetListGenerator.ListImagesSort())
    def ddtest_sort_images_list(self, params):
        """
        @summary: List all images, sorting the list by passing in a query
        parameter as the sort_key and a direction as the sort_dir

        @param params: Parameter being passed to the list images request
        @type params: Dictionary

        1) List all images passing in a query parameter as the sort_key and a
        direction as the sort_dir
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned is in order based on the sort_key
        and sort_dir
        """

        sort_dir = None
        sort_key = None
        not_str_list = ['created_at', 'min_disk', 'min_ram', 'owner', 'size',
                        'updated_at', 'user_id']

        # Only two key-value pairs are passed in, sort_dir and sort_key
        for key in params.keys():
            if key == 'sort_dir':
                sort_dir = params[key]
            elif key == 'sort_key':
                sort_key = params[key]

        # This is a temporary workaround for skips in ddtests
        additional_property = self.images.config.additional_property
        expected_failure_properties = [
            additional_property, 'auto_disk_config', 'id', 'image_type',
            'os_type', 'protected', 'tags', 'user_id', 'visibility']
        if sort_key in expected_failure_properties:
            sys.stderr.write('skipped \'Redmine bugs #11260 and #11262\' ... ')
            return

        listed_images = self.images.behaviors.list_all_images(**params)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for current, next_ in zip(listed_images[0::2], listed_images[1::2]):
            current_item = getattr(current, sort_key)
            next_item = getattr(next_, sort_key)
            if sort_key not in not_str_list:
                if current_item is not None:
                    current_item = current_item.lower()
                if next_item is not None:
                    next_item = next_item.lower()
            if sort_dir.lower() == 'asc':
                self.assertLessEqual(
                    current_item, next_item,
                    msg=('Unexpected items for images {0} and {1} received.'
                         'Expected: Less than or equal to {2} '
                         'Received: {3}').format(next_.id_, current.id_,
                                                 next_item, current_item))
            else:
                self.assertGreaterEqual(
                    current_item, next_item,
                    msg=('Unexpected items for images {0} and {1} received.'
                         'Expected: Greater than or equal to {0} '
                         'Received: {1}').format(next_.id_, current.id_,
                                                 next_item, current_item))

    @unittest.skip('Redmine bug #11261')
    def test_sort_images_list_passing_id_asc(self):
        """
        @summary: List all images, sorting the list by passing in id as the
        sort_key and asc as the sort_dir

        1) List all images passing in id as the sort_key and asc as the
        sort_dir
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for id that is less
        than or equal to the value for id of the next image
        """

        sort_key_var = 'id_'

        api_args = {'sort_key': 'id', 'sort_dir': SortDirection.ASCENDING}

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for current, next_ in zip(listed_images[0::2], listed_images[1::2]):
            current_item = getattr(current, sort_key_var).replace('-', '')
            next_item = getattr(next_, sort_key_var).replace('-', '')

            self.assertLessEqual(
                current_item, next_item,
                msg=('Unexpected item received. Expected: Less than or equal '
                     'to {0} Received: {1}').format(next_item, current_item))

    @unittest.skip('Redmine bug #11261')
    def test_sort_images_list_passing_id_desc(self):
        """
        @summary: List all images, sorting the list by passing in id as the
        sort_key and desc as the sort_dir

        1) List all images passing in id as the sort_key and desc as the
        sort_dir
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned contains a value for id that is
        greater than or equal to the value for id of the next image
        """

        sort_key_var = 'id_'

        api_args = {'sort_key': 'id', 'sort_dir': SortDirection.DESCENDING}

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for current, next_ in zip(listed_images[0::2], listed_images[1::2]):
            current_item = getattr(current, sort_key_var).replace('-', '')
            next_item = getattr(next_, sort_key_var).replace('-', '')

            self.assertGreaterEqual(
                current_item, next_item,
                msg=('Unexpected item received. Expected: Greater than or '
                     'equal to {0} Received: {1}').format(next_item,
                                                          current_item))
