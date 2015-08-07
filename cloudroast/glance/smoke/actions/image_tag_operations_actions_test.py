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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture


class ImageTagOperationsActions(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageTagOperationsActions, cls).setUpClass()

        cls.tag = rand_name('tag')

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={
                'name': rand_name('image_tag_operations_actions')},
            count=2)

        cls.add_image_tag_image = created_images.pop()

        cls.delete_image_tag_image = created_images.pop()
        cls.images.client.add_image_tag(
            cls.delete_image_tag_image.id_, cls.tag)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageTagOperationsActions, cls).tearDownClass()

    def test_add_single_image_tag(self):
        """
        @summary: Add single image tag

        1) Add image tag via add/delete image tag wrapper method
        2) Verify that the added image tag is in the list of image tags
        """

        get_image = self._add_delete_image_tag(self.add_image_tag_image.id_)

        self.assertIn(
            self.tag, get_image.tags,
            msg=('Unexpected tag for image {0} received. '
                 'Expected: {1} in tags Received: {2} '
                 'not in tags').format(self.add_image_tag_image.id_, self.tag,
                                       get_image.tags))

    def test_delete_single_image_tag(self):
        """
        @summary: Delete single image tag

        1) Delete image tag via add/delete image tag wrapper method
        2) Verify that the deleted image tag is not in the list of image tags
        """

        get_image = self._add_delete_image_tag(
            self.delete_image_tag_image.id_, 'delete')

        self.assertNotIn(
            self.tag, get_image.tags,
            msg=('Unexpected tag for image {0} received. '
                 'Expected: {1} in tags Received: {2} '
                 'not in tags').format(self.delete_image_tag_image.id_,
                                       self.tag, get_image.tags))

    def _add_delete_image_tag(self, image_id, api='add'):
        """
        @summary: Add/Delete an image tag and return the get image details
        response

        @param image_id: Image id to add/delete image tag to/from
        @type image_id: Uuid
        @param api: Api action to perform on image
        @type api: String

        @return: Get image details response
        @rtype: Object

        1) Delete image tag
        2) Verify that the response code is 204
        3) Get image details
        4) Verify that the response is ok
        5) Return get image details response
        """

        if api.lower() == 'delete':
            resp = self.images.client.delete_image_tag(image_id, self.tag)
        elif api.lower() == 'add':
            resp = self.images.client.add_image_tag(image_id, self.tag)
        else:
            self.fail('Unexpected api action received. Expected: add or '
                      'delete Received: {0}'.format(api))

        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(image_id)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

        return resp.entity
