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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.exceptions import BadRequest
from cloudroast.compute.fixtures import ComputeFixture


class ImagesListTestNegative(ComputeFixture):

    @tags(type='negative', net='no')
    def test_list_images_filter_by_nonexistent_server_id(self):
        """
        A list of images filtered by nonexistent server id should be empty

        Request a list of images using the server id value of
        'sjlfdlkjfldjlkdjfldjf'. As the test user, use the server id value as the
        server ref filter parameter to request a list of images. Validate that the
        status code for the list images request is 200 and the image list is empty.

        The following assertions occur:
            - The status code of an images list request using a nonexistent
              server id as a filter should be equal to 200
            - The images list returned by the image list request using a
              nonexistent server id as a filter should be empty
        """
        server_id = 'sjlfdlkjfldjlkdjfldjf'
        images = self.images_client.list_images(server_ref=server_id)
        self.assertEqual(200, images.status_code,
                         "The response code is not 200")
        self.assertEqual(0, len(images.entity),
                         "The list of images is not empty.")

    @tags(type='negative', net='no')
    def test_list_images_filter_by_nonexistent_image_name(self):
        """
        A list of images filtered by nonexistent image should be empty

        Request a list of images using the image name value of
        'aljsdjfsjkljlkjdfkjs999'. As the test user, use the image name
        value as the image name filter parameter to request a list of images.
        Validate that the status code for the list images request is 200
        and the image list is empty.

        The following assertions occur:
            - The status code of an images list request using a nonexistent
              image name as a filter should be equal to 200
            - The images list returned by the image list request using a
              nonexistent image name as a filter should be empty
        """
        image_name = 'aljsdjfsjkljlkjdfkjs999'
        images = self.images_client.list_images(image_name=image_name)
        self.assertEqual(200, images.status_code,
                         "The response code is not 200.")
        self.assertEqual(0, len(images.entity),
                         "The list of images is not empty.")

    @tags(type='negative', net='no')
    def test_list_images_filter_by_invalid_image_status(self):
        """
        A list of images filtered by an invalid image status should be empty

        Request a list of images using the image status value of
        'INVALID'. As the test user, use the image status value as the image
        status filter parameter, request a list of images. Validate that the
        status code for the list images request is 200 and the image list is
        empty.

        The following assertions occur:
            - The status code of an images list request using an invalid image
              status as a filter should be equal to 200
            - The images list returned by the image list request using an
              invalid image status as a filter should be empty
        """
        image_status = 'INVALID'
        images = self.images_client.list_images(status=image_status)
        self.assertEqual(200, images.status_code,
                         "The response code is not 200.")
        self.assertEqual(0, len(images.entity),
                         "The list of images is not empty.")

    @tags(type='negative', net='no')
    def test_list_images_filter_by_invalid_marker(self):
        """
        No images should be listed when filtered with an invalid marker

        A request for a list of images with a marker value of 999 should raise
        a BadRequest error.

        The following assertions occur:
            - Requesting a list of images as the test user with an invalid
              marker value of 999 should raise a BadRequest error
        """
        marker = 999
        with self.assertRaises(BadRequest):
            self.images_client.list_images(marker=marker)

    @tags(type='negative', net='no')
    def test_list_images_filter_by_invalid_type(self):
        """
        A list of images filtered by an invalid type should be empty

        Request a list of images using the image type value of
        'INVALID'. As the test user, use the image type value as the image
        status filter parameter to request a list of images. Validate that the
        status code for the list images request is 200 and the image list is
        empty.

        The following assertions occur:
            - The status code of an images list request using an invalid image
              type as a filter should be equal to 200
            - The images list returned by the image list request using an
              invalid image type as a filter should be empty
        """
        type = 'INVALID'
        images = self.images_client.list_images(image_type=type)
        self.assertEqual(200, images.status_code,
                         "The response code is not 200.")
        self.assertEqual(0, len(images.entity),
                         "The list of images is not empty")

    @tags(type='negative', net='no')
    def test_list_images_filter_by_invalid_changes_since(self):
        """
        Images should not be listed when invalid changes since value is provided

        A request for a list of images with a changes since value of
        '22-02-2013' should raise a BadRequest error.

        The following assertions occur:
            - Requesting a list of images as the test user with an invalid
              changes since value of '22-02-2013' should raise a BadRequest
              error
        """
        changes_since = '22-02-2013'
        with self.assertRaises(BadRequest):
            self.images_client.list_images(changes_since=changes_since)

    @tags(type='negative', net='no')
    def test_list_images_filter_by_time_only_changes_since(self):
        """
        Filtering images an incomplete changes since value should fail

        A request for a list of images with a changes since value of 'T12:13Z'
        should raise a BadRequest error.

        The following assertions occur:
            - Requesting a list of images as the test user with a time only
              changes since value of 'T12:13Z' should raise a BadRequest error
        """
        changes_since = 'T12:13Z'
        with self.assertRaises(BadRequest):
            self.images_client.list_images(changes_since=changes_since)

    @tags(type='negative', net='no')
    def test_list_images_filter_by_invalid_limit(self):
        """
        Filtering images with an invalid limit value should fail

        A request for a list of images with a limit value of -3 should raise a
        BadRequest error.

        The following assertions occur:
            - Requesting a list of images as the test user with an invalid
              limit value of -3 should raise a BadRequest error
        """
        limit = -3
        with self.assertRaises(BadRequest):
            self.images_client.list_images(limit=limit)
