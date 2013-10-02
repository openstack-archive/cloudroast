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
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class GetImagesTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_get_images(self):
        """Get images and verify response code is 200."""
        response = self.api_client.list_images()
        self.assertEqual(response.status_code, 200)

    @tags(type='positive')
    def test_get_all_images(self):
        """Get images and verify they exist."""
        response = self.api_client.list_images()
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No default images returned.')

    @tags(type='positive')
    def test_get_images_by_name(self):
        """Get images, filtered by name property"""
        response = self.api_client.list_images(name='cirros-0.3.1-x86_64-uec')
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.name, 'cirros-0.3.1-x86_64-uec')

    @tags(type='positive')
    def test_get_images_by_container_format(self):
        """Get images, filtered by container_format property"""
        response = self.api_client.list_images(container_format='ami')
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.container_format, 'ami')

    @tags(type='positive')
    def test_get_images_by_disk_format(self):
        """Get images, filtered by disk_format property"""
        response = self.api_client.list_images(disk_format='ami')
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(len(images), 0, 'No images returned.')
        for image in images:
            self.assertEqual(image.disk_format, 'ami')

    @tags(type='positive')
    def test_get_images_by_status(self):
        """Get images, filtered by status property"""
        list_response = self.api_client.list_images(status='active')
        images = list_response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')
        for image in images:
            self.assertEqual(image.status, 'active')

    @tags(type='positive')
    def test_get_images_by_visibility(self):
        """Get images, filtered by visibility property"""
        list_response = self.api_client.list_images(visibility='public')
        images = list_response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')
        for image in images:
            self.assertEqual(image.visibility, 'public')

    @tags(type='positive')
    def test_get_images_by_size_min(self):
        """Get images, filtered by size_min property"""
        list_response = self.api_client.list_images(size_min='3714970')
        images = list_response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')
        for image in images:
            self.assertTrue(int(image.size) > 3714969)

    @tags(type='positive')
    def test_get_images_by_size_max(self):
        """Get images, filtered by size_max property"""
        list_response = self.api_client.list_images(size_max='25165820')
        images = list_response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')
        for image in images:
            self.assertTrue(int(image.size) < 25165819)

    @tags(type='positive')
    def test_get_images_by_min_ram(self):
        """Get images, filtered by min_ram property."""
        create_response = self.api_client.create_image(
            name=rand_name('image-test-'),
            min_ram=512,
            container_format='bare',
            disk_format='raw')

        self.assertEqual(create_response.status_code, 201)
        image = create_response.entity
        self.assertIsNotNone(image)
        self.resources.add(image.id_, self.api_client.delete_image)

        list_response = self.api_client.list_images(min_ram=512)
        images = list_response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')
        for image in images:
            self.assertTrue(int(image.min_ram) >= 512)

    @tags(type='positive')
    def test_get_images_by_min_disk(self):
        """Get images, filtered by min_disk property."""
        create_response = self.api_client.create_image(
            name=rand_name('image-test-'),
            min_disk=2048,
            container_format='bare',
            disk_format='raw')

        self.assertEqual(create_response.status_code, 201)
        image = create_response.entity
        self.assertIsNotNone(image)
        self.resources.add(image.id_, self.api_client.delete_image)

        list_response = self.api_client.list_images(min_disk=2048)
        images = list_response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')
        for image in images:
            self.assertTrue(int(image.min_disk) >= 2048)

    @tags(type='positive')
    def test_get_images_by_status_and_disk_format(self):
        """Get images, filtered by status and disk_format properties."""
        response = self.api_client.list_images(status='active',
                                               disk_format='ami')
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')
        for image in images:
            self.assertEqual(image.status, 'active')
            self.assertEqual(image.disk_format, 'ami')

    @tags(type='negative')
    def test_get_images_sorted_by_invalid_key_schema(self):
        """Get images, filtered by an invalid sort key: schema"""
        response = self.api_client.list_images(sort_key='schema')

        self.assertEquals(response.status_code, 400)

    @tags(type='positive')
    def test_get_images_by_name_sort_key(self):
        """Get images, sorted by name."""
        response = self.api_client.list_images(sort_key='name')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(images[i + 1].name <= images[i].name)

    @tags(type='positive')
    def test_get_images_by_status_sort_key(self):
        """Get images, sorted by status."""
        response = self.api_client.list_images(sort_key='status')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(images[i + 1].status <= images[i].status)

    @tags(type='positive')
    def test_get_images_by_container_format_sort_key(self):
        """Get images, sorted by container_format."""
        response = self.api_client.list_images(sort_key='container_format')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].container_format <= images[i].container_format)

    @tags(type='positive')
    def test_get_images_by_disk_format_sort_key(self):
        """Get images, sorted by disk format."""
        response = self.api_client.list_images(sort_key='disk_format')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].disk_format <= images[i].disk_format)

    @tags(type='positive')
    def test_get_images_by_size_sort_key(self):
        """Get images, sorted by size."""
        response = self.api_client.list_images(sort_key='size')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].size <= images[i].size)

    @tags(type='positive')
    def test_get_images_by_id_sort_key(self):
        """Get images, sorted by id."""
        response = self.api_client.list_images(sort_key='id')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].id_ <= images[i].id_)

    @tags(type='positive')
    def test_get_images_by_created_at_sort_key(self):
        """Get images, sorted by created_at."""
        response = self.api_client.list_images(sort_key='created_at')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].created_at <= images[i].created_at)

    @tags(type='positive')
    def test_get_images_by_updated_at_sort_key(self):
        """Get images, sorted by updated_at."""
        response = self.api_client.list_images(sort_key='updated_at')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].updated_at <= images[i].updated_at)

    @tags(type='positive')
    def test_get_images_by_id_sort_key_and_sort_dir_asc(self):
        """Get images, sorted by id and sort direction ascending."""
        response = self.api_client.list_images(sort_key='id',
                                               sort_dir='asc')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].id_ >= images[i].id_)

    @tags(type='positive')
    def test_get_images_by_id_sort_key_and_sort_dir_desc(self):
        """Get images, sorted by id and sort direction descending."""
        response = self.api_client.list_images(sort_key='id',
                                               sort_dir='desc')

        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        for i in range(0, len(images) - 1):
            self.assertTrue(
                images[i + 1].id_ <= images[i].id_)

    @tags(type='positive')
    def test_get_images_by_pagination_marker(self):
        """Get images, paginated by marker."""
        response = self.api_client.list_images()
        self.assertTrue(response.status_code, 200)
        self.assertIsNotNone(response.entity, 'Images deserialization failed.')
        images_list = response.entity
        marker = images_list[0].id_

        response = self.api_client.list_images(marker=marker)
        images = response.entity
        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertNotEqual(0, len(images), 'No images returned.')

        self.assertListEqual(images_list[1:], images[:-1])
        self.assertTrue(marker not in [image.id_ for image in images])

    @tags(type='positive')
    def test_get_images_by_pagination_limit(self):
        """Get images, paginated by limit flag."""
        response = self.api_client.list_images()
        self.assertTrue(response.status_code, 200)
        self.assertIsNotNone(response.entity, 'Images deserialization failed.')
        all_images = response.entity

        for limit in range(0, len(all_images) + 1):
            response = self.api_client.list_images(limit=limit)
            self.assertTrue(response.status_code, 200)
            self.assertIsNotNone(response.entity,
                                 'Images deserialization failed.')
            images = response.entity

            self.assertTrue(len(images) <= limit)

    @tags(type='negative')
    def test_get_images_using_http_method_put(self):
        """Try get images using incorrect HTTP method PUT.

        1. PUT request to /images endpoint
        2. Verify the response code is 404
        """
        self.assertTrue(False, "Not Implemented")
