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

import unittest

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageStatus
from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


@DataDrivenFixture
@unittest.skipUnless(
    images.config.allow_post_images, 'Endpoint has incorrect access')
class UpdateRegisteredImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(UpdateRegisteredImage, cls).setUpClass()

        cls.reg_image = cls.images.behaviors.register_new_image(
            name=rand_name('update_registered_image'))

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(UpdateRegisteredImage, cls).tearDownClass()

    @data_driven_test(ImagesDatasetListGenerator.UpdateImageAllowed(
        image_status=ImageStatus.QUEUED))
    def ddtest_update_reg_image_replace_allowed_property(self, prop):
        """
        @summary: Update image replacing allowed image property

        @param prop: Key-value pair containing the image property to validate
        @type prop: Dictionary

        1) Update image replacing allowed image property's value
        2) Verify that the response code is 200
        3) Verify that the update image response shows that the property's
        value has been updated as expected
        4) Get image details for the image
        5) Verify that the response is ok
        6) Verify that the get image details response shows that the property's
        value has been updated as expected
        7) Verify that the image's updated_at time has increased
        """

        # Each prop passed in only has one key-value pair
        prop_key, prop_val = prop.popitem()

        resp = self.images.client.update_image(
            self.reg_image.id_, replace={prop_key: prop_val})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        updated_image = resp.entity

        self.assertEqual(
            getattr(updated_image, prop_key), prop_val,
            msg=('Unexpected updated image value received. Expected: {0} '
                 'Received: {1}').format(prop_val,
                                         getattr(updated_image, prop_key)))

        resp = self.images.client.get_image_details(self.reg_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            getattr(get_image, prop_key), prop_val,
            msg=('Unexpected get image details value received. Expected: {0} '
                 'Received: {1}').format(prop_val, getattr(get_image,
                                                           prop_key)))

        self.assertGreaterEqual(
            updated_image.updated_at, self.reg_image.updated_at,
            msg=('Unexpected updated_at value received. '
                 'Expected: Greater than {0} '
                 'Received: {1}').format(self.reg_image.updated_at,
                                         updated_image.updated_at))
