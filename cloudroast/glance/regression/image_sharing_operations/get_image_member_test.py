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

from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture


class GetImageMember(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(GetImageMember, cls).setUpClass()

        cls.member_id = cls.images_alt_one.auth.tenant_id

        created_images = cls.images.behaviors.create_images_via_task(count=3)

        cls.shared_image = created_images.pop()
        resp = cls.images.client.create_image_member(
            cls.shared_image.id_, cls.member_id)
        cls.created_member = resp.entity

        cls.accepted_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.accepted_image.id_, cls.member_id)
        resp = cls.images_alt_one.client.update_image_member(
            cls.accepted_image.id_, cls.member_id, ImageMemberStatus.ACCEPTED)
        cls.accepted_member = resp.entity

        cls.rejected_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.rejected_image.id_, cls.member_id)
        resp = cls.images_alt_one.client.update_image_member(
            cls.rejected_image.id_, cls.member_id, ImageMemberStatus.REJECTED)
        cls.rejected_member = resp.entity

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(GetImageMember, cls).tearDownClass()

    def test_get_image_member(self):
        """
        @summary: Get image member

        1) Get image member
        2) Verify that the response code is 200
        3) Verify that the member received for the get image member matches the
        member received for the create image member
        """

        resp = self.images.client.get_image_member(
            self.shared_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        get_member = resp.entity

        errors = self._validate_get_image_member(
            get_member, self.created_member)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.shared_image.id_, errors))

    def test_get_image_member_as_member_image_shared_with(self):
        """
        @summary: Get image member as a member the image is shared with

        1) Get image member as member of the shared image
        2) Verify that the response code is 200
        3) Verify that the member received for the get image member matches the
        member received for the create image member
        """

        resp = self.images_alt_one.client.get_image_member(
            self.shared_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        get_member = resp.entity

        errors = self._validate_get_image_member(
            get_member, self.created_member)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.shared_image.id_, errors))

    def test_get_image_member_accepted_image(self):
        """
        @summary: Get image member of an image that has been accepted

        1) Get image member of an image that as been accepted
        2) Verify that the response code is 200
        3) Verify that the member received for the get image member matches the
        member received for the updated accepted image member
        """

        resp = self.images.client.get_image_member(
            self.accepted_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        get_member = resp.entity

        errors = self._validate_get_image_member(
            get_member, self.accepted_member)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.accepted_image.id_, errors))

    def test_get_image_member_rejected_image(self):
        """
        @summary: Get image member of an image that has been rejected

        1) Get image member of an image that as been rejected
        2) Verify that the response code is 200
        3) Verify that the member received for the get image member matches the
        member received for the updated rejected image member
        """

        resp = self.images.client.get_image_member(
            self.rejected_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        get_member = resp.entity

        errors = self._validate_get_image_member(
            get_member, self.rejected_member)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.rejected_image.id_, errors))

    def test_get_image_member_as_tenant_without_access_to_image(self):
        """
        @summary: Get image member of image as tenant without access to the
        image

        1) Get image member as tenant without access to the image
        2) Verify that the response code is 404
        3) Verify that no image member is returned
        """

        resp = self.images_alt_two.client.get_image_member(
            self.shared_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

        self.assertEqual(
            resp.reason, 'Not Found',
            msg='Unexpected image members returned. Expected: Not Found '
                'Received: {0}'.format(resp.reason))

    def test_get_image_member_using_blank_image_id(self):
        """
        @summary: Get image member using blank image id

        1) Get image member using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_member(
            image_id='', member_id=self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_get_image_member_using_invalid_image_id(self):
        """
        @summary: Get image member using invalid image id

        1) Get image member using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_member(
            image_id='invalid', member_id=self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_get_image_member_using_blank_member_id(self):
        """
        @summary: Get image member using blank member id

        1) Get image member using blank member id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_member(
            image_id=self.shared_image.id_, member_id='')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_get_image_member_using_invalid_member_id(self):
        """
        @summary: Get image member using invalid member id

        1) Get image member using invalid member id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_member(
            image_id=self.shared_image.id_, member_id='invalid')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def _validate_get_image_member(self, get_member, created_member):
        """
        @summary: Validate that the member received for the get image member
        request and the member received for the create image member match

        @param get_member: Image member received for the get image member
        request
        @type get_member: Object
        @param created_member: Image member received for the create image
        member request
        @type created_member: Object

        @return: Errors
        @rtype: List
        """

        errors = []

        if get_member.created_at != created_member.created_at:
            errors.append(self.error_msg.format(
                'created_at', created_member.created_at,
                get_member.created_at))
        if get_member.image_id != created_member.image_id:
            errors.append(self.error_msg.format(
                'image_id', created_member.image_id, get_member.image_id))
        if get_member.member_id != created_member.member_id:
            errors.append(self.error_msg.format(
                'member_id', created_member.member_id,
                get_member.member_id))
        if get_member.schema != created_member.schema:
            errors.append(self.error_msg.format(
                'schema', created_member.schema, get_member.schema))
        if get_member.status != created_member.status:
            errors.append(self.error_msg.format(
                'status', created_member.status, get_member.status))
        if get_member.updated_at != created_member.updated_at:
            errors.append(self.error_msg.format(
                'updated_at', created_member.updated_at,
                get_member.updated_at))

        return errors
