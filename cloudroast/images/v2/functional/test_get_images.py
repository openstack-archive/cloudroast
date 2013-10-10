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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.constants import Messages
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.images.v2.fixtures import ImagesV2Fixture

msg = Messages.ASSERT_MSG
SIZE_MIN = 3714970
SIZE_MAX = 25165820
MIN_RAM = 512
MIN_DISK = 2048


class GetImagesTest(ImagesV2Fixture):
    """ Tests for the GET /v2/images endpoint."""

    @tags(type='smoke')
    def test_get_images(self):
        """Get images and verify response code is 200.

        1. Get a list of images
        2. Verify the response code is 200
        """
        response = self.api_client.list_images()
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

    @tags(type='positive')
    def test_get_all_images(self):
        """Get images and verify they exist.

        1. Get a list of images
        2. Verify that the list is not empty
        """
        response = self.api_client.list_images()
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No default images returned.')

    @tags(type='positive')
    def test_get_images_by_name(self):
        """Get images, filtered by name property.

        1. Get a list of images with a specific name
        2. Verify the list is not empty
        3. Verify the images returned have the specified name.
        """
        response = self.api_client.list_images(name='cirros-0.3.1-x86_64-uec')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.name, 'cirros-0.3.1-x86_64-uec',
                             'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_container_format(self):
        """Get images, filtered by container_format property.

        1. Get a list of images with specific container format
        2. Verify the list is not empty
        3. Verify the images returned have specified container format
        """
        response = self.api_client.list_images(container_format='ami')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.container_format, 'ami',
                             'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_disk_format(self):
        """Get images, filtered by disk_format property.

        1. Get a list of images with specific disk format
        2. Verify the list is not empty
        3. Verify the images returned have specified disk format
        """
        response = self.api_client.list_images(disk_format='ami')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.disk_format, 'ami',
                             'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_status(self):
        """Get images, filtered by status property.

        1. Get a list of images with specific status
        2. Verify the list is not empty
        3. Verify the images returned have specified status
        """
        response = self.api_client.list_images(status='active')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.status, 'active',
                             'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_visibility(self):
        """Get images, filtered by visibility property.

        1. Get a list of images with specific visibility
        2. Verify the list is not empty
        3. Verify the images returned have specified visibility"""
        response = self.api_client.list_images(visibility='public')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.visibility, 'public',
                             'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_size_min(self):
        """Get images, filtered by size_min property.

        1. Get a list of images with specific size_min
        2. Verify the list is not empty
        3. Verify the images returned have specified size_min
        """
        response = self.api_client.list_images(size_min=SIZE_MIN)
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertTrue(int(image.size) > SIZE_MIN - 1,
                            'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_size_max(self):
        """Get images, filtered by size_max property

        1. Get a list of images with specific size_max
        2. Verify the list is not empty
        3. Verify the images returned have specified size_max
        """
        response = self.api_client.list_images(size_max=SIZE_MAX)
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertTrue(int(image.size) < SIZE_MAX - 1,
                            'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_min_ram(self):
        """Get images, filtered by min_ram property.

        1. Get a list of images with specific min_ram
        2. Verify the list is not empty
        3. Verify the images returned have specified min_ram
        """
        response = self.api_client.create_image(
            name=rand_name('image-test-'),
            min_ram=MIN_RAM,
            container_format='bare',
            disk_format='raw')
        self.assertEqual(response.status_code, 201,
                         msg.format('status_code', 201, response.status_code))

        image = response.entity
        self.assertIsNotNone(image)
        self.resources.add(image.id_, self.api_client.delete_image)

        response = self.api_client.list_images(min_ram=MIN_RAM)
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertTrue(int(image.min_ram) >= MIN_RAM,
                            'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_min_disk(self):
        """Get images, filtered by min_disk property.

        1. Get a list of images with specific min_disk
        2. Verify the list is not empty
        3. Verify the images returned have specified min_disk
        """
        response = self.api_client.create_image(
            name=rand_name('image-test-'),
            min_disk=MIN_DISK,
            container_format='bare',
            disk_format='raw')
        self.assertEqual(response.status_code, 201,
                         msg.format('status_code', 201, response.status_code))

        image = response.entity
        self.assertIsNotNone(image)
        self.resources.add(image.id_, self.api_client.delete_image)

        response = self.api_client.list_images(min_disk=MIN_DISK)
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertTrue(int(image.min_disk) >= MIN_DISK,
                            'Incorrect images returned.')

    @tags(type='positive')
    def test_get_images_by_status_and_disk_format(self):
        """Get images, filtered by status and disk_format properties.

        1. Get a list of images by specific status and disk_format
        2. Verify the list is not empty
        3. Verify the images returned have specified status and disk_format
        """
        response = self.api_client.list_images(status='active',
                                               disk_format='ami')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.status, 'active',
                             'Incorrect images returned.')
            self.assertEqual(image.disk_format, 'ami',
                             'Incorrect images returned.')

    @tags(type='negative')
    def test_get_images_sorted_by_invalid_key_schema(self):
        """Get images, sorted by an invalid sort key.

        1. Get a list of images, sorted by invalid sort key
        2. Verify the response code is 400
        """
        response = self.api_client.list_images(sort_key='schema')
        self.assertEquals(response.status_code, 400)

    @tags(type='positive')
    def test_get_images_by_name_sort_key(self):
        """Get images, sorted by name.

        1. Get a list of images sorted by name
        2. Verify the list is not empty
        3. Verify the list is sorted by name
        """
        response = self.api_client.list_images(sort_key='name')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.name, next.name)

    @tags(type='positive')
    def test_get_images_by_status_sort_key(self):
        """Get images, sorted by status.

        1. Get a list of images sorted by status
        2. Verify the list is not empty
        3. Verify the list is sorted by status.
        """
        response = self.api_client.list_images(sort_key='status')
        self.assertEqual(response.status_code, 200,
                     msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.status, next.status)

    @tags(type='positive')
    def test_get_images_by_container_format_sort_key(self):
        """Get images, sorted by container_format.

        1. Get a list of images sorted by container format
        2. Verify the list is not empty
        3. Verify the list is sorted by container format.
        """
        response = self.api_client.list_images(sort_key='container_format')
        self.assertEqual(response.status_code, 200,
                 msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.container_format,
                                    next.container_format)

    @tags(type='positive')
    def test_get_images_by_disk_format_sort_key(self):
        """Get images, sorted by disk format.

        1. Get a list of images sorted by disk format
        2. Verify the list is not empty
        3. Verify the list is sorted by disk format.
        """
        response = self.api_client.list_images(sort_key='disk_format')
        self.assertEqual(response.status_code, 200,
                 msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.disk_format, next.disk_format)

    @tags(type='positive')
    def test_get_images_by_size_sort_key(self):
        """Get images, sorted by size.

        1. Get a list of images sorted by size
        2. Verify the list is not empty
        3. Verify the list is sorted by size.
        """
        response = self.api_client.list_images(sort_key='size')
        self.assertEqual(response.status_code, 200,
                 msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.size, next.size)

    @tags(type='positive')
    def test_get_images_by_id_sort_key(self):
        """Get images, sorted by id.

        1. Get a list of images sorted by id
        2. Verify the list is not empty
        3. Verify the list is sorted by id
        """
        response = self.api_client.list_images(sort_key='id')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertLessEqual(current.id_, next.id_)

    @tags(type='positive')
    def test_get_images_by_created_at_sort_key(self):
        """Get images, sorted by created_at.

        1. Get a list of images sorted by created_at
        2. Verify the list is not empty
        3. Verify the list is sorted by created_at
        """
        response = self.api_client.list_images(sort_key='created_at')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.created_at, next.created_at)

    @tags(type='positive')
    def test_get_images_by_updated_at_sort_key(self):
        """Get images, sorted by updated_at.

        1. Get a list of images sorted by updated_at
        2. Verify the list is not empty
        3. Verify the list is sorted by updated_at
        """
        response = self.api_client.list_images(sort_key='updated_at')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.updated_at, next.updated_at)

    @tags(type='positive')
    def test_get_images_by_id_sort_key_and_sort_dir_asc(self):
        """Get images, sorted by id and sort direction ascending.

        1. Get a list of images sorted by id in ascending order
        2. Verify the list is not empty
        3. Verify the list is sorted by id in ascending order
        """
        response = self.api_client.list_images(sort_key='id',
                                               sort_dir='asc')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertLessEqual(current.id_, next.id_)

    @tags(type='positive')
    def test_get_images_by_id_sort_key_and_sort_dir_desc(self):
        """Get images, sorted by id and sort direction descending.

        1. Get a list of images sorted by id in descending order
        2. Verify the list is not empty
        3. Verify the list is sorted by id in descending order
        """
        response = self.api_client.list_images(sort_key='id',
                                               sort_dir='desc')
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        for current, next in zip(images[0::2], images[1::2]):
            self.assertLessEqual(current.id_, next.id_)

    @tags(type='positive')
    def test_get_images_by_pagination_marker(self):
        """Get images, paginated by marker.

        1. Get images, paginated by marker
        2. Verify the list is not empty
        3. Verify the list is paginated by marker.
        """
        response = self.api_client.list_images()
        self.assertEquals(response.status_code, 200,
                         msg.format('status_code', 200, response.status_code))

        self.assertIsNotNone(response.entity, 'Images deserialization failed.')
        images_list = response.entity
        marker = images_list[0].id_

        response = self.api_client.list_images(marker=marker)
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')

        self.assertListEqual(images_list[1:len(images)], images[:-1])
        self.assertTrue(marker not in [image.id_ for image in images])

    @tags(type='positive')
    def test_get_images_by_pagination_limit(self):
        """Get images, paginated by limit flag.

        1. Get list of images by limit
        2. Verify the list is not empty
        3. Get a list of images with different limits
        4. Verify each list contains no more than specified limits
        """
        response = self.api_client.list_images()
        self.assertTrue(response.status_code, 200)
        self.assertIsNotNone(response.entity, 'Images deserialization failed.')
        all_images = response.entity

        for limit in enumerate(all_images):
            response = self.api_client.list_images(limit=limit)
            self.assertTrue(response.status_code, 200)
            self.assertIsNotNone(response.entity,
                                 'Images deserialization failed.')
            images = response.entity

            self.assertLessEqual(len(images), limit)

    @tags(type='negative')
    def test_get_images_using_http_method_put(self):
        """Try get images using incorrect HTTP method PUT.

        1. PUT request to /images endpoint
        2. Verify the response code is 404
        """
        self.assertTrue(False, "Not Implemented")
