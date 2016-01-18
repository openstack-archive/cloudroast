"""
Copyright 2016 Rackspace

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

import datetime
from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages

from cloudcafe.glance.common.types import (
    ImageMemberStatus, ImageType, ImageVisibility, SortDirection)

from cloudroast.glance.fixtures import ImagesIntegrationFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class ListImages(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(ListImages, cls).setUpClass()

        cls.alt_one_member = cls.images_alt_one.auth.tenant_id

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('list_images')}, count=4)

        cls.created_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.created_image.id_, cls.alt_one_member)
        resp = cls.images.client.get_image_member(
            cls.created_image.id_, cls.alt_one_member)
        cls.created_image_member = resp.entity

        cls.shared_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.shared_image.id_, cls.alt_one_member)

        image = created_images.pop()
        cls.images_admin.client.deactivate_image(image.id_)
        cls.deactivated_imported_image = (
            cls.images.client.get_image_details(image.id_)).entity

        alt_image = created_images.pop()
        cls.images_admin.client.deactivate_image(alt_image.id_)
        cls.images_admin.client.reactivate_image(alt_image.id_)
        cls.reactivated_imported_image = (
            cls.images.client.get_image_details(alt_image.id_)).entity

        created_server = cls.compute.servers.behaviors.create_active_server(
            image_ref=cls.images.config.primary_image).entity
        cls.resources.add(
            created_server.id, cls.compute.servers.client.delete_server)

        snapshot_image = cls.compute.images.behaviors.create_active_image(
            created_server.id).entity
        cls.resources.add(snapshot_image.id, cls.images.client.delete_image)
        cls.images_admin.client.deactivate_image(snapshot_image.id)
        cls.deactivated_snapshot_image = (
            cls.images.client.get_image_details(snapshot_image.id).entity)

        alt_snapshot_image = cls.compute.images.behaviors.create_active_image(
            created_server.id).entity
        cls.resources.add(
            alt_snapshot_image.id, cls.images.client.delete_image)
        cls.images_admin.client.deactivate_image(alt_snapshot_image.id)
        cls.images_admin.client.reactivate_image(alt_snapshot_image.id)
        cls.reactivated_snapshot_image = (
            cls.images.client.get_image_details(alt_snapshot_image.id).entity)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ListImages, cls).tearDownClass()

    def test_compare_list_images_between_glance_and_nova(self):
        """
        @summary: Compare the list of images returned from the glance api and
        the nova api

        1) List images with a limit set to 100 and image_type set to base
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
            params={'limit': 100, 'image_type': ImageType.BASE})
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

        glance_image_names = [image.name for image in resp.entity]
        self.assertIsNotNone(
            glance_image_names, msg=('Unexpected images received.'
                                     'Expected: At least one image received '
                                     'Received: No images received'))

        resp = self.compute.images.client.list_images_with_detail(
            limit=100, image_type='base')
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

        nova_image_names = [image.name for image in resp.entity]
        self.assertIsNotNone(
            nova_image_names, msg=('Unexpected images received.'
                                   'Expected: At least one image received '
                                   'Received: No images received'))

        self.assertEqual(
            len(nova_image_names), len(glance_image_names),
            msg=('Unexpected images received. Expected: Number of Nova images '
                 '({0}) to match number of Glance images ({1}) Received: '
                 'Number of images do not '
                 'match'.format(len(nova_image_names),
                                len(glance_image_names))))

        images_diff = list(
            set(glance_image_names) - set(nova_image_names))
        self.assertEqual(images_diff, [],
                         msg=('Unexpected images listed in Glance that are '
                              'not listed in Nova: {0}').format(images_diff))

    def test_image_visibility_of_shared_images(self):
        """
        @summary: Image visibility of shared images

        1) Using alt_one_member, list all images
        2) Verify that shared_image is not present
        3) Using alt_one_member, list all images passing visibility as shared
        and member status as all
        4) Verify that shared_image is now present
        5) Using alt_one_member, update image member status to rejected
        6) Verify that the response is ok
        7) Using alt_one_member, list all images passing visibility as shared
        and member status as all
        8) Verify that shared_image is still present
        """

        listed_images = self.images_alt_one.behaviors.list_all_images()
        self.assertNotIn(
            self.shared_image, listed_images,
            msg=('Unexpected image received. Expected: {0} to not be in list '
                 'of images Received: {1}').format(self.shared_image,
                                                   listed_images))

        listed_images = self.images_alt_one.behaviors.list_all_images(
            visibility=ImageVisibility.SHARED,
            member_status=ImageMemberStatus.ALL)
        self.assertIn(
            self.shared_image, listed_images,
            msg=('Expected image not received. Expected: {0} to be in list of '
                 'images Received: {1}').format(self.shared_image,
                                                listed_images))

        resp = self.images_alt_one.client.update_image_member(
            self.shared_image.id_, self.alt_one_member,
            ImageMemberStatus.REJECTED)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

        listed_images = self.images_alt_one.behaviors.list_all_images(
            visibility=ImageVisibility.SHARED,
            member_status=ImageMemberStatus.ALL)
        self.assertIn(
            self.shared_image, listed_images,
            msg=('Expected image not received. Expected: {0} to be in list of '
                 'images Received: {1}').format(self.shared_image,
                                                listed_images))

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

        api_args = {}

        for param in params:
            if param == 'id_':
                api_args.update({'id': getattr(self.created_image, param)})
            elif param == 'created_at' or param == 'updated_at':
                # Params will always only have a single value
                api_args.update({param: 'lte:{0}'.format(params[param])})
            else:
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
                if param == 'created_at' or param == 'updated_at':
                    # Params will always only have a single value
                    received = datetime.datetime.strptime(
                        str(received), '%Y-%m-%d %H:%M:%S+00:00')
                    expected = datetime.datetime.strptime(
                        params[param], '%Y-%m-%dT%H:%M:%SZ')
                    self.assertLessEqual(
                        received, expected,
                        msg=('Unexpected property value for image {0} '
                             'received. Expected: {1} '
                             'Received: {2}').format(image.id_, expected,
                                                     received))
                else:
                    self.assertEqual(
                        received, expected,
                        msg=('Unexpected property value for image {0} '
                             'received. Expected: {1} '
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

    def test_filter_images_list_passing_member_status_pending(self):
        """
        @summary: List all images that match in member_status of pending and
        visibility of shared as the query parameters

        1) List all images passing in member_status of pending and visibility
        of shared as the query parameters
        2) Verify that the list of images returned is not empty
        3) Verify that each image returned list image members
        4) Verify that each image returned contains a value for member_status
        that matches the member_status that is being used as the filter
        """

        api_args = (
            {'member_status': getattr(self.created_image_member, 'status'),
             'visibility': ImageVisibility.SHARED})

        listed_images = self.images_alt_one.behaviors.list_all_images(
            **api_args)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        for image in listed_images:
            image_member_statuses = []
            resp = self.images.client.list_image_members(image.id_)
            self.assertTrue(resp.ok,
                            Messages.OK_RESP_MSG.format(resp.status_code))
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
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

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
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

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
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

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
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

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
        @summary: List all base images, sorting the list by passing in a query
        parameter as the sort_key and a direction as the sort_dir

        @param params: Parameter being passed to the list images request
        @type params: Dictionary

        1) List all base images passing in a query parameter as the sort_key
        and a direction as the sort_dir
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

        params.update({'image_type': ImageType.BASE})

        listed_images = self.images.behaviors.list_all_images(**params)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        if sort_key == 'id':
            sort_key = 'id_'

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
                         'Expected: Greater than or equal to {2} '
                         'Received: {3}').format(next_.id_, current.id_,
                                                 next_item, current_item))

    def test_sort_images_list_using_multiple_sort_keys_only(self):
        """
        @summary: List all images, sorting the list by passing in multiple
        query parameters as the sort_keys only

        1) List all images passing in multiple query parameters as the
        sort_keys only via wrapper test method
        2) Verify that each image returned is in order based on the first
        sort_key (descending by default)
        3) If the two images being compared have the same value for the first
        sort_key, verify that each image returned in then in order based on the
        second sort_key (descending by default)
        """

        listed_images = self._list_images_with_sort_keys_dirs(
            ['created_at', 'size'])

        for current, next_ in zip(listed_images[0::2], listed_images[1::2]):
            self.assertGreaterEqual(
                current.created_at, next_.created_at,
                msg=('Unexpected order of images {0} and {1} received. '
                     'Expected: Greater than or equal to {2} Received: '
                     '{3}').format(next_.id_, current.id_, next_.created_at,
                                   current.created_at))

            # If created_at dates are equal, verify sizes are in expected order
            if current.created_at == next_.created_at:
                self.assertGreaterEqual(
                    current.size, next_.size,
                    msg=('Unexpected order of images {0} and {1} received.'
                         'Expected: Greater than or equal to {2} Received: '
                         '{3}').format(next_.id_, current.id_, next_.size,
                                       current.size))

    def test_sort_images_list_using_multiple_sort_keys_and_sort_dirs(self):
        """
        @summary: List all images, sorting the list by passing in multiple
        query parameters as the sort_keys and multiple directions as the
        sort_dirs

        1) List all images passing in multiple query parameters as the
        sort_keys and multiple directions as the sort_dirs via wrapper test
        method
        2) Verify that each image returned is in order based on the first
        sort_key and sort_dir
        3) Verify that each image returned in then in order based on the second
        sort_key and sort_dir
        """

        listed_images = self._list_images_with_sort_keys_dirs(
            ['name', 'size'],
            [SortDirection.ASCENDING, SortDirection.DESCENDING])

        for current, next_ in zip(listed_images[0::2], listed_images[1::2]):
            current_name = current.name
            next_name = next_.name
            if current_name is not None:
                current_name = current_name.lower()
            if next_name is not None:
                next_name = next_name.lower()

            self.assertLessEqual(
                next_name, next_name,
                msg=('Unexpected order of images {0} and {1} received.'
                     'Expected: Less than or equal to {2} Received: '
                     '{3}').format(next_.id_, current.id_, next_name,
                                   current_name))

            if current_name == next_name:
                self.assertGreaterEqual(
                    current.size, next_.size,
                    msg=('Unexpected order of images {0} and {1} received.'
                         'Expected: Greater than or equal to {2} Received: '
                         '{3}').format(next_.id_, current.id_, next_.size,
                                       current.size))

    def test_sort_images_list_using_multi_sort_keys_and_single_sort_dir(self):
        """
        @summary: List all images, sorting the list by passing in multiple
        query parameters as the sort_keys and a single direction as the
        sort_dir

        1) List all images passing in multiple query parameters as the
        sort_keys and a single direction as the sort_dir via wrapper test
        method
        2) Verify that each image returned is in order based on the first
        sort_key and sort_dir
        3) Verify that each image returned in then in order based on the second
        sort_key and the same sort_dir
        """

        listed_images = self._list_images_with_sort_keys_dirs(
            ['created_at', 'size'], [SortDirection.ASCENDING])

        for current, next_ in zip(listed_images[0::2], listed_images[1::2]):
            self.assertLessEqual(
                current.created_at, next_.created_at,
                msg=('Unexpected order of images {0} and {1} received.'
                     'Expected: Less than or equal to {2} Received: '
                     '{3}').format(next_.id_, current.id_, next_.created_at,
                                   current.created_at))

            if current.created_at == next_.created_at:
                self.assertLessEqual(
                    current.size, next_.size,
                    msg=('Unexpected order of images {0} and {1} received.'
                         'Expected: Less than or equal to {2} Received: '
                         '{3}').format(next_.id_, current.id_, next_.size,
                                       current.size))

    def test_sort_images_list_using_multiple_sort_dirs_only(self):
        """
        @summary: List all images, sorting the list by passing in multiple
        query parameters as the sort_dirs only

        1) List all images passing in multiple query parameters as the
        sort_dirs only
        2) Verify that the response code is 400
        """

        sort_dirs = [SortDirection.ASCENDING, SortDirection.DESCENDING]

        sort_pairs = ['sort_dir={0}'.format(key) for key in sort_dirs]

        url_addition = '&'.join(sort_pairs)

        resp = self.images.client.list_images(url_addition=url_addition)
        self.assertEqual(
            resp.status_code, 400,
            Messages.STATUS_CODE_MSG.format(400, resp.status_code))

    def test_sort_images_list_using_single_sort_key_and_multi_sort_dirs(self):
        """
        @summary: List all images, sorting the list by passing in a single
        query parameter as the sort_key and multiple query parameters as the
        sort_dirs

        1) List all images passing in a single query parameter as the sort_key
        and multiple query parameters as the sort_dirs
        2) Verify that the response code is 400
        """

        sort_key = 'name'
        sort_dirs = [SortDirection.ASCENDING, SortDirection.DESCENDING]

        sort_pairs = ['sort_dir={0}'.format(key) for key in sort_dirs]
        sort_pairs.append('sort_key={0}'.format(sort_key))

        url_addition = '&'.join(sort_pairs)

        resp = self.images.client.list_images(url_addition=url_addition)
        self.assertEqual(
            resp.status_code, 400,
            Messages.STATUS_CODE_MSG.format(400, resp.status_code))

    def test_list_deactivated_images(self):
        """
        @summary: List all images with no additional query parameters,
        paginating through the results as needed, and verify that the
        deactivated images are listed

        1) List all images via wrapper test method
        2) Verify that there are no errors
        """

        errors = self._verify_listed_images([
            self.deactivated_imported_image, self.deactivated_snapshot_image])

        self.assertEqual(
            errors, [],
            msg=('Unexpected errors received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_list_reactivated_images(self):
        """
        @summary: List all images with no additional query parameters,
        paginating through the results as needed, and verify that the
        reactivated images are listed

        1) List all images via wrapper test method
        2) Verify that there are no errors
        """

        errors = self._verify_listed_images([
            self.reactivated_imported_image, self.reactivated_snapshot_image])

        self.assertEqual(
            errors, [],
            msg=('Unexpected errors received. Expected: No errors '
                 'Received: {0}').format(errors))

    def _verify_listed_images(self, expected_images):
        """
        @summary: List all images with no additional query parameters,
        paginating through the results as needed, and verify that the
        expected images are listed

        @param expected_images: Images to expect
        @type expected_images: List

        @return: Errors
        @rtype: List

        1) List all images not passing in any additional query parameter,
        paginating through the results as needed
        2) Verify that the list is not empty
        3) Verify that the expected images are in the returned list of
        images
        4) Return errors
        """

        listed_images = self.images.behaviors.list_all_images()

        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        return [('Expected image not received. Expected: {0} in list of '
                 'images Received: {1}').format(image.id_, listed_images)
                for image in expected_images if image not in listed_images]

    def _list_images_with_sort_keys_dirs(self, sort_keys, sort_dirs=None):
        """
        @summary: List all images, sorting the list by passing in query
        parameters for the sort_keys and sort_dirs and return the list of
        images

        @param sort_keys: Keys to sort an image list by
        @type sort_keys: List
        @param sort_dirs: Directions to sort an image list by
        @type sort_dirs: Object

        @return: Listed images
        @rtype: List

        1) List all images passing in query parameters for the sort_keys and
        sort_dirs
        2) Verify that the list of images returned is not empty
        3) Return the list of images
        """

        sort_pairs = [
            'sort_key={0}'.format(sort_key) for sort_key in sort_keys]
        if sort_dirs is not None:
            [sort_pairs.append('sort_dir={0}'.format(sort_dir))
             for sort_dir in sort_dirs]

        url_addition = '&'.join(sort_pairs)

        listed_images = self.images.behaviors.list_all_images(url_addition)
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        return listed_images
