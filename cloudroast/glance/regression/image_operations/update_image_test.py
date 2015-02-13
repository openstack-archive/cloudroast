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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class UpdateImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(UpdateImage, cls).setUpClass()
        created_images = cls.images.behaviors.create_images_via_task(count=2)
        cls.created_image = created_images.pop()
        cls.alt_created_image = created_images.pop()

    @classmethod
    def tearDownClass(cls):
        cls.images.client.update_image(
            cls.created_image.id_, replace={'protected': False})
        cls.images.behaviors.resources.release()
        super(UpdateImage, cls).tearDownClass()

    @data_driven_test(
        ImagesDatasetListGenerator.UpdateImageAllowed())
    def ddtest_update_image_replace_allowed_property(self, prop):
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
        for key, value in prop.iteritems():
            prop_key = key
            prop_val = value

        resp = self.images.client.update_image(
            self.created_image.id_, replace={prop_key: prop_val})
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        updated_image = resp.entity

        self.assertEqual(
            getattr(updated_image, prop_key), prop_val,
            msg=('Unexpected updated image value received. Expected: {0} '
                 'Received: {1}').format(prop_val,
                                         getattr(updated_image, prop_key)))

        resp = self.images.client.get_image_details(self.created_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            getattr(get_image, prop_key), prop_val,
            msg=('Unexpected get image details value received. Expected: {0} '
                 'Received: {1}').format(prop_val,
                                         getattr(get_image, prop_key)))

        self.assertGreaterEqual(
            updated_image.updated_at, self.created_image.updated_at,
            msg=('Unexpected updated_at value received. '
                 'Expected: Greater than {0} '
                 'Received: {1}').format(self.created_image.updated_at,
                                         updated_image.updated_at))

    @data_driven_test(
        ImagesDatasetListGenerator.UpdateImageInaccessible())
    def ddtest_update_image_replace_inaccessible_property(self, prop):
        """
        @summary: Update image replacing inaccessible image property

        @param prop: Key-value pair containing the image property to validate
        @type prop: Dictionary

        1) Update image replacing inaccessible image property's value
        2) Verify that the response code is 403
        """

        # Each prop passed in only has one key-value pair
        for key, value in prop.iteritems():
            prop_key = key
            prop_val = value

        resp = self.images.client.update_image(
            self.alt_created_image.id_, replace={prop_key: prop_val})
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

    @data_driven_test(
        ImagesDatasetListGenerator.UpdateImageRestricted())
    def ddtest_update_image_replace_restricted_property(self, prop):
        """
        @summary: Update image replacing restricted image property

        @param prop: Key-value pair containing the image property to validate
        @type prop: Dictionary

        1) Update image replacing restricted image property's value
        2) Verify that the response code is 403
        3) Get image details for the image
        4) Verify that the response is ok
        5) Verify that the get image details response shows that the property's
        value has not been updated
        """

        # Each prop passed in only has one key-value pair
        for key, value in prop.iteritems():
            prop_key = key
            prop_val = value

        # This is a temporary workaround for skips in ddtests
        if prop_key == 'id':
            sys.stderr.write('skipped \'Redmine bug #11398\' ... ')
            return

        resp = self.images.client.update_image(
            self.alt_created_image.id_, replace={prop_key: prop_val})
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

        resp = self.images.client.get_image_details(self.alt_created_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        prop_key = self._check_prop_key(prop_key)

        self.assertEqual(
            getattr(get_image, prop_key),
            getattr(self.alt_created_image, prop_key),
            msg=('Unexpected get image details value received. Expected: {0} '
                 'Received: {1}').format(getattr(self.alt_created_image,
                                                 prop_key),
                                         getattr(get_image, prop_key)))

    @data_driven_test(
        ImagesDatasetListGenerator.UpdateImageRestricted())
    def ddtest_update_image_add_restricted_property(self, prop):
        """
        @summary: Update image adding restricted image property

        @param prop: Key-value pair containing the image property to validate
        @type prop: Dictionary

        1) Update image adding restricted image property
        2) Verify that the response code is 403
        3) Get image details for the image
        4) Verify that the response is ok
        5) Verify that the get image details response shows that the property
        has been not been added
        """

        # Each prop passed in only has one key-value pair
        for key, value in prop.iteritems():
            prop_key = key
            prop_val = value

        # # This is a temporary workaround for skips in ddtests
        if prop_key == 'id':
            sys.stderr.write('skipped \'Redmine bug #11398\' ... ')
            return

        resp = self.images.client.update_image(
            self.alt_created_image.id_, add={prop_key: prop_val})
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

        resp = self.images.client.get_image_details(self.alt_created_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        prop_key = self._check_prop_key(prop_key)

        self.assertEqual(
            getattr(get_image, prop_key), getattr(self.alt_created_image,
                                                  prop_key),
            msg=('Unexpected get image details value received. Expected: {0} '
                 'Received: {1}').format(getattr(self.alt_created_image,
                                                 prop_key),
                                         getattr(get_image, prop_key)))

    @data_driven_test(
        ImagesDatasetListGenerator.UpdateImageRestricted())
    def ddtest_update_image_remove_restricted_property(self, prop):
        """
        @summary: Update image removing restricted image property

        @param prop: Key-value pair containing the image property to validate
        @type prop: Dictionary

        1) Update image removing restricted image property
        2) Verify that the response code is 403
        3) Get image details for the image
        4) Verify that the response is ok
        5) Verify that the get image details response shows that the property
        has been not been removed
        """

        # Each prop passed in only has one key-value pair
        for key, value in prop.iteritems():
            prop_key = key
            prop_val = value

        # This is a temporary workaround for skips in ddtests
        if prop_key == 'id':
            sys.stderr.write('skipped \'Redmine bug #11398\' ... ')
            return
        if prop_key == 'file' or prop_key == 'schema' or prop_key == 'self':
            sys.stderr.write('skipped \'Redmine bug #11403\' ... ')
            return
        if prop_key == 'location':
            sys.stderr.write('skipped \'Redmine bug #11\' ... ')
            return

        resp = self.images.client.update_image(
            self.alt_created_image.id_, remove={prop_key: prop_val})
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

        resp = self.images.client.get_image_details(self.alt_created_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        prop_key = self._check_prop_key(prop_key)

        self.assertEqual(
            getattr(get_image, prop_key), getattr(self.alt_created_image,
                                                  prop_key),
            msg=('Unexpected get image details value received. Expected: {0} '
                 'Received: {1}').format(getattr(self.alt_created_image,
                                                 prop_key),
                                         getattr(get_image, prop_key)))

    def test_update_image_add_new_property(self):
        """
        @summary: Update image by adding a new image property

        1) Update image adding a new image property
        2) Verify that the response code is 200
        3) Verify that the update image response shows that the new property
        has been added as expected
        4) Get image details for the image
        5) Verify that the response is ok
        6) Verify that the get image details response shows that the new
        property has been added as expected
        """

        new_property = 'new_property'
        new_property_value = rand_name('new_property_value')

        resp = self.images.client.update_image(
            self.created_image.id_, add={new_property: new_property_value})
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        updated_image = resp.entity

        self.assertIn(
            new_property, updated_image.additional_properties,
            msg=('Unexpected new image property received. Expected: {0} to be '
                 'present '
                 'Received: {1}').format(new_property,
                                         updated_image.additional_properties))
        for prop, prop_val in updated_image.additional_properties.iteritems():
            if prop == new_property:
                self.assertEqual(
                    prop_val, new_property_value,
                    msg=('Unexpected new image property value received. '
                         'Expected: {0} '
                         'Received: {1}').format(new_property_value, prop_val))

        resp = self.images.client.get_image_details(self.created_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        self.assertIn(
            new_property, get_image.additional_properties,
            msg=('Unexpected new image property received. Expected: {0} to be '
                 'present '
                 'Received: {1}').format(new_property,
                                         get_image.additional_properties))
        for prop, prop_val in get_image.additional_properties.iteritems():
            if prop == new_property:
                self.assertEqual(
                    prop_val, new_property_value,
                    msg=('Unexpected new image property value received. '
                         'Expected: {0} '
                         'Received: {1}').format(new_property_value, prop_val))

    def test_update_image_remove_property(self):
        """
        @summary: Update image by removing an image property

        1) Update image adding a new image property
        2) Verify that the response code is 200
        3) Update the image removing the new image property
        4) Verify that the response code is 200
        5) Verify that the update image response shows that the new
        property has been removed as expected
        6) Get image details for the image
        7) Verify that the response code is ok
        8) Verify that the get image response shows that the new
        property has been removed as expected
        """

        new_property = 'alt_new_property'
        new_property_value = rand_name('alt_new_property_value')

        resp = self.images.client.update_image(
            self.created_image.id_, add={new_property: new_property_value})
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

        response = self.images.client.update_image(
            self.created_image.id_, remove={new_property: new_property_value})
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        updated_image = response.entity

        self.assertNotIn(
            new_property, updated_image.additional_properties,
            msg=('Unexpected removed image property received. Expected: {0} '
                 'to not be present '
                 'Received: {1}').format(new_property,
                                         updated_image.additional_properties))

        resp = self.images.client.get_image_details(self.created_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        self.assertNotIn(
            new_property, get_image.additional_properties,
            msg=('Unexpected removed image property received. Expected: {0} '
                 'to not be present '
                 'Received: {1}').format(new_property,
                                         get_image.additional_properties))

    def test_update_image_replace_additional_property(self):
        """
        @summary: Update image by replacing an additional image property

        1) Update image adding a new image property
        2) Verify that the response code is 200
        3) Update the image replacing the new image property's value
        4) Verify that the response code is 200
        5) Verify that the update image response shows that the new property's
        value has been updated as expected
        6) Get image details for the image
        7) Verify that the response code is ok
        8) Verify that the get image response shows that the new
        property's value has been updated as expected
        """

        new_property = 'alt_two_new_property'
        new_property_value = rand_name('alt_two_new_property_value')
        updated_property_value = rand_name('updated_new_property_value')

        resp = self.images.client.update_image(
            self.created_image.id_, add={new_property: new_property_value})
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

        resp = self.images.client.update_image(
            self.created_image.id_,
            replace={new_property: updated_property_value})
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        updated_image = resp.entity

        self.assertIn(
            new_property, updated_image.additional_properties,
            msg=('Unexpected new image property received. Expected: {0} to be '
                 'present '
                 'Received: {1}').format(new_property,
                                         updated_image.additional_properties))
        for prop, prop_val in updated_image.additional_properties.iteritems():
            if prop == new_property:
                self.assertEqual(
                    prop_val, updated_property_value,
                    msg=('Unexpected new image property value received. '
                         'Expected: {0} '
                         'Received: {1}').format(updated_property_value,
                                                 prop_val))

        resp = self.images.client.get_image_details(self.created_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        self.assertIn(
            new_property, get_image.additional_properties,
            msg=('Unexpected new image property received. Expected: {0} to be '
                 'present '
                 'Received: {1}').format(new_property,
                                         get_image.additional_properties))
        for prop, prop_val in get_image.additional_properties.iteritems():
            if prop == new_property:
                self.assertEqual(
                    prop_val, updated_property_value,
                    msg=('Unexpected new image property value received. '
                         'Expected: {0} '
                         'Received: {1}').format(updated_property_value,
                                                 prop_val))

    def test_update_image_using_blank_image_id(self):
        """
        @summary: Update image using a blank image id

        1) Update image using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.update_image(
            image_id='', add={'new_prop': rand_name('new_prop_value')})
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_update_image_using_invalid_image_id(self):
        """
        @summary: Update image using an invalid image id

        1) Update image using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.update_image(
            image_id='invalid', add={'new_prop': rand_name('new_prop_value')})
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def _check_prop_key(self, prop_key):
        """
        @summary: Check if prop_key needs an underscore added

        @param prop_key: Image property to check
        @type prop_key: String

        @return: Prop_key
        @rtype: String
        """

        keys_need_underscore = ['file', 'id', 'self']

        if prop_key in keys_need_underscore:
            prop_key = '{0}_'.format(prop_key)

        if prop_key == 'location':
            prop_key = 'file_'

        return prop_key
