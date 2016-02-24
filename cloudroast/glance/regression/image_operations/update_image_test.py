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

import sys

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class UpdateImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(UpdateImage, cls).setUpClass()

        cls.new_prop = rand_name('new_property')
        cls.new_prop_value = rand_name('new_property_value')
        cls.updated_prop_value = rand_name('updated_new_property_value')

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('update_image')}, count=9)

        cls.created_image = created_images.pop()
        cls.alt_created_image = created_images.pop()
        cls.quota_image = created_images.pop()

        cls.add_prop_deactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(
            cls.add_prop_deactivated_image.id_)

        cls.replace_prop_deactivated_image = created_images.pop()
        cls.images.client.update_image(
            cls.replace_prop_deactivated_image.id_,
            add={cls.new_prop: cls.new_prop_value})
        cls.images_admin.client.deactivate_image(
            cls.replace_prop_deactivated_image.id_)

        cls.remove_prop_deactivated_image = created_images.pop()
        cls.images.client.update_image(
            cls.remove_prop_deactivated_image.id_,
            add={cls.new_prop: cls.new_prop_value})
        cls.images_admin.client.deactivate_image(
            cls.remove_prop_deactivated_image.id_)

        cls.add_prop_reactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(
            cls.add_prop_reactivated_image.id_)
        cls.images_admin.client.reactivate_image(
            cls.add_prop_reactivated_image.id_)

        cls.replace_prop_reactivated_image = created_images.pop()
        cls.images.client.update_image(
            cls.replace_prop_reactivated_image.id_,
            add={cls.new_prop: cls.new_prop_value})
        cls.images_admin.client.deactivate_image(
            cls.replace_prop_reactivated_image.id_)
        cls.images_admin.client.reactivate_image(
            cls.replace_prop_reactivated_image.id_)

        cls.remove_prop_reactivated_image = created_images.pop()
        cls.images.client.update_image(
            cls.remove_prop_reactivated_image.id_,
            add={cls.new_prop: cls.new_prop_value})
        cls.images_admin.client.deactivate_image(
            cls.remove_prop_reactivated_image.id_)
        cls.images_admin.client.deactivate_image(
            cls.remove_prop_reactivated_image.id_)

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
        prop_key, prop_val = prop.popitem()

        resp = self.images.client.update_image(
            self.created_image.id_, replace={prop_key: prop_val})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        updated_image = resp.entity

        self.assertEqual(
            getattr(updated_image, prop_key), prop_val,
            msg=('Unexpected updated image value received. Expected: {0} '
                 'Received: {1}').format(prop_val,
                                         getattr(updated_image, prop_key)))

        resp = self.images.client.get_image_details(self.created_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
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
        prop_key, prop_val = prop.popitem()

        resp = self.images.client.update_image(
            self.alt_created_image.id_, replace={prop_key: prop_val})
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

    @data_driven_test(
        ImagesDatasetListGenerator.UpdateReplaceImageRestricted())
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
        prop_key, prop_val = prop.popitem()

        resp = self.images.client.update_image(
            self.alt_created_image.id_, replace={prop_key: prop_val})
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(self.alt_created_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
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
        ImagesDatasetListGenerator.UpdateAddRemoveImageRestricted())
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
        prop_key, prop_val = prop.popitem()

        if prop_key == 'visibility':
            sys.stderr.write('skipped \'Launchpad bug #1443512\' ... ')
            return
        if prop_key == 'owner':
            sys.stderr.write('skipped \'Launchpad bug #1541594\' ... ')
            return

        resp = self.images.client.update_image(
            self.alt_created_image.id_, add={prop_key: prop_val})
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(self.alt_created_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
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
        ImagesDatasetListGenerator.UpdateAddRemoveImageRestricted())
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

        failure_prop_list = [
            'id', 'file', 'location', 'schema', 'self']

        # Each prop passed in only has one key-value pair
        prop_key, prop_val = prop.popitem()

        # This is a temporary workaround for skips in ddtests
        if prop_key in failure_prop_list:
            sys.stderr.write('skipped \'Launchpad bug #1443563\' ... ')
            return

        resp = self.images.client.update_image(
            self.alt_created_image.id_, remove={prop_key: prop_val})
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(self.alt_created_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        prop_key = self._check_prop_key(prop_key)

        self.assertEqual(
            getattr(get_image, prop_key), getattr(self.alt_created_image,
                                                  prop_key),
            msg=('Unexpected get image details value received. Expected: {0} '
                 'Received: {1}').format(getattr(self.alt_created_image,
                                                 prop_key),
                                         getattr(get_image, prop_key)))

    def test_update_image_replace_additional_property(self):
        """
        @summary: Update image by replacing an additional image property

        1) Update image adding a new image property
        2) Verify that the response code is 200
        3) Update the image replacing the new image property's value via
        wrapper test method
        4) Verify that the new image's property's value has been updated as
        expected
        """

        new_prop = 'alt_two_new_property'
        new_prop_value = rand_name('alt_two_new_property_value')

        resp = self.images.client.update_image(
            self.created_image.id_, add={new_prop: new_prop_value})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        replaced_prop_value = self._update_image_add_replace_property(
            self.created_image.id_, 'replace', new_prop)

        self.assertEqual(
            replaced_prop_value, self.updated_prop_value,
            msg=('Unexpected updated image property value received. '
                 'Expected: {0} '
                 'Received: {1}').format(self.updated_prop_value,
                                         replaced_prop_value))

    def test_update_image_remove_property(self):
        """
        @summary: Update image by removing an image property

        1) Update image adding a new image property
        2) Verify that the response code is 200
        3) Update reactivated image removing an image property via test
        wrapper method
        4) Verify that the image property has been removed as expected
        """

        new_prop = 'alt_new_property'

        resp = self.images.client.update_image(
            self.created_image.id_, add={new_prop: self.new_prop_value})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        get_image = self._update_image_remove_property(
            self.created_image.id_, new_prop)

        self.assertNotIn(
            new_prop, get_image.additional_properties,
            msg=('Unexpected removed image property received. Expected: {0} '
                 'to not be present '
                 'Received: {1}').format(new_prop,
                                         get_image.additional_properties))

    def test_update_deactivated_image_add_property(self):
        """
        @summary: Update deactivated image by adding an image property

        1) Update deactivated image adding an image property via wrapper test
        method
        2) Verify that the property has been added as expected
        """

        added_prop_value = self._update_image_add_replace_property(
            self.add_prop_deactivated_image.id_)

        self.assertEqual(
            added_prop_value, self.new_prop_value,
            msg=('Unexpected new image property value received. Expected: {0} '
                 'Received: '
                 '{1}').format(self.new_prop_value, added_prop_value))

    def test_update_deactivated_image_replace_property(self):
        """
        @summary: Update deactivated image by replacing an image property

        1) Update deactivated image replacing an image property's value via
        wrapper test method
        2) Verify that the image's property's value has been updated as
        expected
        """

        replaced_prop_value = self._update_image_add_replace_property(
            self.replace_prop_deactivated_image.id_, 'replace')

        self.assertEqual(
            replaced_prop_value, self.updated_prop_value,
            msg=('Unexpected updated image property value received.'
                 'Expected: {0} '
                 'Received: {1}').format(self.updated_prop_value,
                                         replaced_prop_value))

    def test_update_deactivated_image_remove_property(self):
        """
        @summary: Update deactivated image by removing an image property

        1) Update deactivated image removing an image property via test
        wrapper method
        2) Verify that the image property has been removed as expected
        """

        get_image = self._update_image_remove_property(
            self.remove_prop_deactivated_image.id_)

        self.assertNotIn(
            self.new_prop, get_image.additional_properties,
            msg=('Unexpected removed image property received. Expected: {0} '
                 'to not be present '
                 'Received: {1}').format(self.new_prop,
                                         get_image.additional_properties))

    def test_update_reactivated_image_add_property(self):
        """
        @summary: Update reactivated image by adding an image property

        1) Update reactivated image adding an image property via wrapper test
        method
        2) Verify that the property has been added as expected
        """

        added_prop_value = self._update_image_add_replace_property(
            self.add_prop_reactivated_image.id_)

        self.assertEqual(
            added_prop_value, self.new_prop_value,
            msg=('Unexpected new image property value received. Expected: {0} '
                 'Received: '
                 '{1}').format(self.new_prop_value, added_prop_value))

    def test_update_reactivated_image_replace_property(self):
        """
        @summary: Update reactivated image by replacing an image property

        1) Update reactivated image replacing an image property's value via
        wrapper test method
        2) Verify that the image's property's value has been updated as
        expected
        """

        replaced_prop_value = self._update_image_add_replace_property(
            self.replace_prop_reactivated_image.id_, 'replace')

        self.assertEqual(
            replaced_prop_value, self.updated_prop_value,
            msg=('Unexpected updated image property value received.'
                 'Expected: {0} '
                 'Received: {1}').format(self.updated_prop_value,
                                         replaced_prop_value))

    def test_update_reactivated_image_remove_property(self):
        """
        @summary: Update reactivated image by removing an image property

        1) Update reactivated image removing an image property via test
        wrapper method
        2) Verify that the image property has been removed as expected
        """

        get_image = self._update_image_remove_property(
            self.remove_prop_reactivated_image.id_)

        self.assertNotIn(
            self.new_prop, get_image.additional_properties,
            msg=('Unexpected removed image property received. Expected: {0} '
                 'to not be present '
                 'Received: {1}').format(self.new_prop,
                                         get_image.additional_properties))

    def test_update_image_property_quota_limit(self):
        """
        @summary: Validate image properties quota limit

        1) While the number of image properties is not equal to the image
        properties quota, update image adding a new image property
        2) Verify that the response code is 200
        3) When the number of image properties is equal to the image properties
        quota, update image adding another new image property
        4) Verify that the response code is 413
        5) Get image details
        6) Verify that the response is ok
        7) Verify that the number of image properties matches the image
        properties quota
        """

        number_of_image_properties = 0
        additional_props = ['auto_disk_config', 'image_type', 'os_type',
                            'user_id']
        quota_limit = self.images.config.image_properties_limit

        # Decrease quota limit for every property that image already contains
        for prop in additional_props:
            if hasattr(self.quota_image, prop):
                quota_limit -= 1

        while number_of_image_properties != quota_limit:
            new_prop = rand_name('prop')
            new_prop_value = rand_name('prop_value')

            resp = self.images.client.update_image(
                self.quota_image.id_, add={new_prop: new_prop_value})
            self.assertEqual(
                resp.status_code, 200,
                Messages.STATUS_CODE_MSG.format(200, resp.status_code))

            resp = self.images.client.get_image_details(self.quota_image.id_)
            self.assertTrue(resp.ok,
                            Messages.OK_RESP_MSG.format(resp.status_code))
            get_image = resp.entity

            number_of_image_properties = len(getattr(get_image,
                                                     'additional_properties'))

        new_prop = rand_name('prop')
        new_prop_value = rand_name('prop_value')

        resp = self.images.client.update_image(
            self.quota_image.id_, add={new_prop: new_prop_value})
        self.assertEqual(
            resp.status_code, 413,
            Messages.STATUS_CODE_MSG.format(413, resp.status_code))

        resp = self.images.client.get_image_details(self.quota_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            len(getattr(get_image, 'additional_properties')), quota_limit,
            msg='Unexpected number of image properties returned.'
                'Expected: {0} '
                'Received: {1}'.format(quota_limit,
                                       len(getattr(get_image,
                                                   'additional_properties'))))

    def test_update_image_using_blank_image_id(self):
        """
        @summary: Update image using a blank image id

        1) Update image using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.update_image(
            image_id='', add={'new_prop': rand_name('new_prop_value')})
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_update_image_using_invalid_image_id(self):
        """
        @summary: Update image using an invalid image id

        1) Update image using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.update_image(
            image_id='invalid', add={'new_prop': rand_name('new_prop_value')})
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

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

    def _update_image_add_replace_property(self, image_id, action='add',
                                           new_prop=None):
        """
        @summary: Update image by adding or replacing an image property and
        return the added or replaced image property

        @param image_id: Image id to update
        @type image_id: Uuid
        @param action: Update image action to perform
        @type action: String
        @param new_prop: New image property to add
        @type new_prop: String

        @return: Get image details properties
        @rtype: String

        1) Update an image adding or replacing an image property
        2) Verify that the response code is 200
        3) Verify that the update image response shows that the property has
        been added or replaced as expected
        4) Get image details for the image
        5) Verify that the response code is ok
        6) Return the added property
        """

        if new_prop is None:
            new_prop = self.new_prop
        prop_value = self.new_prop_value

        if action == 'replace':
            prop_value = self.updated_prop_value
            resp = self.images.client.update_image(
                image_id, replace={new_prop: prop_value})
        else:
            resp = self.images.client.update_image(
                image_id, add={new_prop: prop_value})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        updated_image = resp.entity

        new_prop_value = (
            updated_image.additional_properties.get(new_prop, None))

        self.assertEqual(
            new_prop_value, prop_value,
            msg=('Unexpected new image property value received. Expected: {0} '
                 'Received: '
                 '{1}').format(prop_value, new_prop_value))

        resp = self.images.client.get_image_details(image_id)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        return get_image.additional_properties.get(new_prop, None)

    def _update_image_remove_property(self, image_id, new_prop=None):
        """
        @summary: Update image by removing an image property and return the get
        image details response

        @param image_id: Image id to update
        @type image_id: Uuid

        @return: Get image details
        @rtype: Object

        1) Update an image removing an image property
        2) Verify that the response code is 200
        3) Verify that the update image response shows that the property has
        been removed as expected
        4) Get image details for the image
        5) Verify that the response code is ok
        6) Return the get image details response
        """

        if new_prop is None:
            new_prop = self.new_prop

        resp = self.images.client.update_image(
            image_id, remove={new_prop: self.new_prop_value})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        updated_image = resp.entity

        self.assertNotIn(
            new_prop, updated_image.additional_properties,
            msg=('Unexpected removed image property received. Expected: {0} '
                 'to not be present '
                 'Received: {1}').format(new_prop,
                                         updated_image.additional_properties))

        resp = self.images.client.get_image_details(image_id)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

        return resp.entity
