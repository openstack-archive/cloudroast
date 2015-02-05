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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.types import ImageStatus, ImageVisibility

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
            msg=('Unexpected number of images received. Expected: Not {0}, '
                 'Received: {1}').format(0, len(listed_images)))

        self.assertIn(
            self.created_image, listed_images,
            msg=('Unexpected images received. Expected: {0} in list of '
                 'images, '
                 'Received: {1}').format(self.created_image, listed_images))

        # TODO: Add additional assertions to verify all images are as expected
        for image in listed_images:
            self.assertEqual(
                image.status, ImageStatus.ACTIVE,
                msg=('Unexpected status received. Expected: {0}, '
                     'Received: {1}').format(ImageStatus.ACTIVE, image.status))

    # TODO: Redmine bug 11168 and 11270 opened for property failures
    @data_driven_test(
        ImagesDatasetListGenerator.ListImagesFilters())
    def ddtest_filter_images_list(self, params):
        """
        @summary: List all images that match a filter, passing in a specific
        query parameter

        @param params: Parameter being passed to the list images request
        @type params: Dictionary

        1) List subset of images passing in a query parameter
        2) Verify that each image returned contains a value for the given
        filter(s) that is acceptable
        """

        self._verify_filtered_images_list(params.keys())

    # TODO: Redmine bugs 11260, 11261, and 11262 opened for property failures
    @data_driven_test(
        ImagesDatasetListGenerator.ListImagesSort())
    def ddtest_sort_images_list(self, params):
        """
        @summary: List all images, sorting the list by passing in a specific
        query parameter

        @param params: Parameter being passed to the list images request
        @type params: Dictionary

        1) List subset of images passing in a query parameter
        2) Verify that each image returned contains a value for the given
        filter(s) that is acceptable
        """

        self._verify_sorted_images_list(params)

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
            msg=('Unexpected number of images received. Expected: {0}, '
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
            msg=('Unexpected number of images received. Expected: {0}, '
                 'Received: {1}').format(1, len(next_listed_image)))

        self.assertNotEqual(
            listed_image[0], next_listed_image[0],
            msg=('Unexpected images received. Expected: Images to not match, '
                 'Received: Images match'))

    def test_list_images_using_limit(self):
        """
        @summary: List images using limit

        1) List images passing in 50 as the limit
        2) Verify that the response code is ok
        3) Verify that the list is not empty
        4) Verify that the number of images returned in 50 or less
        """

        resp = self.images.client.list_images(params={'limit': 50})
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_images = resp.entity
        self.assertLessEqual(
            len(listed_images), 50,
            msg=('Unexpected number of images received. Expected: Less than '
                 'or equal to {0}, '
                 'Received: {1}').format(50, len(listed_images)))

    def test_compare_list_images_between_glance_and_nova(self):
        """
        @summary: Compare the list of images returned from the glance api and
        the nova api

        1) List images with a limit of 100 through the glance api
        2) Verify that the response is ok
        3) Remove test images from the list of images returned
        4) List images with a limit of 100 through the nova api
        5) Verify that the response is ok
        6) Verify that the length of the list of images is the same through the
        glance api and the nova api
        7) Verify that each image name in the list of images is the same
        through the glance api and the nova api
        """

        test_image_name = self.images.config.test_image_name

        resp = self.images.client.list_images(
            params={'limit': 100, 'visibility': ImageVisibility.PUBLIC})
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        glance_images = resp.entity
        for image in glance_images:
            if image.name == test_image_name:
                glance_images.remove(image)

        glance_image_names = [image.name for image in glance_images]

        resp = self.compute.images.client.list_images_with_detail(
            limit=100, image_type='base')
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        nova_images = resp.entity
        nova_image_names = [image.name for image in nova_images]

        self.assertEqual(
            len(glance_images), len(nova_images),
            msg=('Unexpected images received. Expected: Number of images to '
                 'match, Received: Number of images do not match'))

        for image_name in glance_image_names:
            self.assertIn(
                image_name, nova_image_names,
                msg=('Unexpected images received. Expected: {0} in list of '
                     'images, '
                     'Received: {1}').format(image_name, nova_image_names))

    def _verify_filtered_images_list(self, parameters):
        """
        @summary: Verify that each image returned contains a value for the
        given filter(s) that is acceptable

        @param parameters: Parameters being validated against a list of images
        @type parameters: List
        """

        api_args = {}

        for param in parameters:
            # Set api_args
            if param == 'size_min' or param == 'size_max':
                api_args.update(
                    {param: getattr(self.images.config, param)})
            else:
                if param == 'member_status':
                    api_args.update(
                        {param: getattr(self.created_image_member, 'status')})
                elif param == 'tag':
                    api_args.update(
                        {param: getattr(self.created_image, 'tags')})
                elif param == self.images.config.additional_property:
                    api_args.update(
                        {param:
                         self.created_image.additional_properties.get(param)})
                else:
                    api_args.update(
                        {param: getattr(self.created_image, param)})

        listed_images = self.images.behaviors.list_all_images(**api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0}, '
                 'Received: {1}').format(0, len(listed_images)))

        for param in parameters:
            # Set attribute
            attribute = param
            if param == 'size_min' or param == 'size_max':
                attribute = 'size'

            # Validate each returned image
            for image in listed_images:
                if param == 'size_min':
                    received_size_min = getattr(image, attribute)
                    expected_size_min = getattr(self.images.config, param)
                    self.assertGreaterEqual(
                        received_size_min, expected_size_min,
                        msg=('Unexpected size_min received. Expected: Greater '
                             'than or equal to {0}, '
                             'Received: {1}').format(expected_size_min,
                                                     received_size_min))
                elif param == 'size_max':
                    received_size_max = getattr(image, attribute)
                    expected_size_max = getattr(self.images.config, param)
                    self.assertLessEqual(
                        received_size_max, expected_size_max,
                        msg=('Unexpected size_max received. Expected: Less '
                             'than or equal to {0}, '
                             'Received: {1}').format(expected_size_max,
                                                     received_size_max))
                else:
                    if param == 'member_status':
                        image_member_statuses = []
                        resp = self.images.client.list_image_members(image.id_)
                        self.assertTrue(resp.ok,
                                        self.ok_resp_msg.format(
                                            resp.status_code))
                        list_image_members = resp.entity
                        for member in list_image_members:
                            image_member_statuses.append(member.status)
                        received_image_member_status = (
                            getattr(self.created_image_member, 'status'))
                        self.assertIn(
                            getattr(self.created_image_member, 'status'),
                            image_member_statuses,
                            msg=('Unexpected image member status received. '
                                 'Expected: {0} in list of image member '
                                 'statuses, Received: '
                                 '{1}').format(received_image_member_status,
                                               image_member_statuses))
                    elif param == 'tag':
                        received_tags = getattr(image, 'tags')
                        expected_tags = getattr(self.created_image, 'tags')
                        self.assertEqual(
                            received_tags, expected_tags,
                            msg=('Unexpected tags received. Expected: {0}, '
                                 'Received: {1}').format(expected_tags,
                                                         received_tags))
                    elif param == self.images.config.additional_property:
                        received_prop = image.additional_properties.get(param)
                        expected_prop = (
                            self.created_image.additional_properties.get(
                                param))
                        self.assertEqual(
                            received_prop, expected_prop,
                            msg=('Unexpected property received. Expected: '
                                 '{0}, Received: {1}').format(expected_prop,
                                                              received_prop))
                    else:
                        received_prop = getattr(image, attribute)
                        expected_prop = getattr(self.created_image, param)
                        self.assertEqual(
                            received_prop, expected_prop,
                            msg=('Unexpected property received. Expected: '
                                 '{0}, Received: {1}').format(expected_prop,
                                                              received_prop))

    def _verify_sorted_images_list(self, parameters):
        """
        @summary: Verify that the images are returned in the expected order
        using the given parameters

        @param parameters: Parameters being used to sort a list of images
        @type parameters: List
        """

        sort_dir = None
        sort_key = None
        not_str_list = ['created_at', 'min_disk', 'min_ram', 'owner', 'size',
                        'updated_at', 'user_id']

        for key in parameters.keys():
            if key == 'sort_dir':
                sort_dir = parameters[key]
            elif key == 'sort_key':
                sort_key = parameters[key]

        listed_images = self.images.behaviors.list_all_images(**parameters)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0}, '
                 'Received: {1}').format(0, len(listed_images)))

        if sort_key.lower() == 'id':
            sort_key = 'id_'
        for current, next_ in zip(listed_images[0::2], listed_images[1::2]):
            current_item = getattr(current, sort_key)
            next_item = getattr(next_, sort_key)
            if sort_key not in not_str_list:
                if current_item is not None:
                    current_item = current_item.lower()
                if next_item is not None:
                    next_item = next_item.lower()
            if sort_key == 'id':
                current_item = current_item.replace('-', '')
                next_item = next_item.replace('-', '')
            if sort_dir.lower() == 'asc':
                self.assertLessEqual(
                    current_item, next_item,
                    msg=('Unexpected item received. Expected: Less than '
                         'or equal to {0}, '
                         'Received: {1}').format(next_item, current_item))
            else:
                self.assertGreaterEqual(
                    current_item, next_item,
                    msg=('Unexpected item received. Expected: Greater than '
                         'or equal to {0}, '
                         'Received: {1}').format(next_item, current_item))
