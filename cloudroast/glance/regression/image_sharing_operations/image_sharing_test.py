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

from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import (
    ImageMemberStatus, ImageType, TaskStatus, TaskTypes)

from cloudroast.glance.fixtures import ImagesIntegrationFixture


class ImageSharing(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageSharing, cls).setUpClass()

        cls.alt_one_member_id = cls.images_alt_one.auth.tenant_id
        cls.alt_two_member_id = cls.images_alt_two.auth.tenant_id

        created_images = cls.images.behaviors.create_images_via_task(count=4)

        cls.single_member_image = created_images.pop()
        cls.multiple_members_image = created_images.pop()

        cls.delete_access_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.delete_access_image.id_, cls.alt_one_member_id)

        cls.no_export_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.no_export_image.id_, cls.alt_one_member_id)

        cls.imported_image = cls.images.behaviors.create_image_via_task(
            import_from=cls.images.config.import_from_bootable)
        cls.images.client.create_image_member(
            cls.imported_image.id_, cls.alt_one_member_id)

        cls.snapshot_image = cls.images.behaviors.create_image_via_task(
            import_from=cls.images.config.import_from_bootable)
        cls.images.client.create_image_member(
            cls.snapshot_image.id_, cls.alt_one_member_id)
        cls.snapshot_server = (
            cls.compute_alt_one_servers_behaviors.create_active_server(
                image_ref=cls.snapshot_image.id_)).entity
        cls.resources.add(
            cls.snapshot_server.id,
            cls.compute_alt_one_servers_client.delete_server)

        cls.alt_snapshot_image = cls.images.behaviors.create_image_via_task(
            import_from=cls.images.config.import_from_bootable)
        cls.images.client.create_image_member(
            cls.alt_snapshot_image.id_, cls.alt_one_member_id)
        cls.export_server = (
            cls.compute_alt_one_servers_behaviors.create_active_server(
                image_ref=cls.alt_snapshot_image.id_)).entity
        cls.resources.add(
            cls.export_server.id,
            cls.compute_alt_one_servers_client.delete_server)
        cls.exported_snapshot = (
            cls.compute_alt_one_images_behaviors.create_active_image(
                cls.export_server.id).entity)
        cls.resources.add(
            cls.exported_snapshot.id, cls.images_alt_one.client.delete_image)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        cls.resources.release()
        super(ImageSharing, cls).tearDownClass()

    def test_delete_shared_image_accessibility(self):
        """
        @summary: Delete shared image accessibility

        1) Get image member alt_one_member for delete_access_image
        2) Verify that the member status is pending
        3) Using alt_one_member, attempt to delete delete_access_image
        4) Verify that the response is a 403
        5) Using alt_one_member, update image member status to accepted
        6) Using alt_one_member, attempt to delete delete_access_image
        7) Verify that the response is a 403
        8) Using image owner, delete delete_access_image
        9) Verify that the response is ok
        10) Using alt_one_member, get image details of delete_access_image
        11) Verify that the response code is a 404
        """

        resp = self.images.client.get_image_member(
            self.delete_access_image.id_, self.alt_one_member_id)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_member = resp.entity

        self.assertEqual(get_member.status, ImageMemberStatus.PENDING)

        resp = self.images_alt_one.client.delete_image(
            self.delete_access_image.id_)
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

        resp = self.images_alt_one.client.update_image_member(
            self.delete_access_image.id_, self.alt_one_member_id,
            ImageMemberStatus.ACCEPTED)
        updated_member = resp.entity

        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)

        resp = self.images_alt_one.client.delete_image(
            self.delete_access_image.id_)
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

        resp = self.images.client.delete_image(
            self.delete_access_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        resp = self.images_alt_one.client.get_image_details(
            self.delete_access_image.id_)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_share_image_with_single_member(self):
        """
        @summary: Share image with single member

        1) Using image owner, get image details of single_member_image
        2) Verify that the single_member_image's properties are as expected
        generically
        3) Using alt_one_member, get image details of single_member_image,
        which is owned by another user and not shared
        4) Verify that the response code is a 404
        5) Using alt_one_member, list images
        6) Verify that the response is ok
        7) Verify that single_member_image is not present
        8) Using image owner, share single_member_image with alt_one_member
        9) Verify that the member status is pending
        10) Using alt_one_member, get image details of single_member_image
        11) Verify that alt_one_member can now access single_member_image
        12) Verify that the get image details response from the image owner
        matches the get image details response of alt_one_member
        13) Using alt_one_member, list images
        14) Verify that the response is ok
        15) Verify that single_member_image is still not present
        16) Using alt_one_member, update image member status to accepted
        17) Using alt_one_member, get image details of single_member_image
        18) Verify that the response is ok
        19) Verify that the get image details response matches the get image
        details response of alt_one_member as before
        20) Using alt_one_member, list images
        21) Verify that the response is ok
        22) Verify that single_member_image is now present
        23) List image members of single_member_image
        24) Verify that the response is ok
        25) Verify that one image member exists
        26) Verify that alt_one_member is present in the image members list
        """

        image_member_ids = []

        resp = self.images.client.get_image_details(
            self.single_member_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image_as_owner = resp.entity

        errors = self.images.behaviors.validate_image(get_image_as_owner)

        self.assertEqual(
            errors, [],
            msg=('Unexpected errors received. Expected: No errors '
                 'Received: {0}').format(errors))

        resp = self.images_alt_one.client.get_image_details(
            self.single_member_image.id_)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

        listed_images = self.images_alt_one.behaviors.list_all_images()
        self.assertNotIn(
            self.single_member_image, listed_images,
            msg='Unexpected images received. Expected: {0} to not be present '
                'Received: Image present'.format(self.single_member_image))

        resp = self.images.client.create_image_member(
            self.single_member_image.id_, self.alt_one_member_id)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        member = resp.entity

        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        resp = self.images_alt_one.client.get_image_details(
            self.single_member_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image_as_member = resp.entity

        self.assertEqual(
            get_image_as_member, get_image_as_owner,
            msg='Unexpected image details received. '
                'Expected: Image details to match '
                'Received: {0} and {1}'.format(get_image_as_member,
                                               get_image_as_owner))

        listed_images = self.images_alt_one.behaviors.list_all_images()
        self.assertNotIn(
            self.single_member_image, listed_images,
            msg='Unexpected images received. Expected: {0} to not be present '
                'Received: Image present'.format(self.single_member_image))

        resp = self.images_alt_one.client.update_image_member(
            self.single_member_image.id_, self.alt_one_member_id,
            ImageMemberStatus.ACCEPTED)
        updated_member = resp.entity

        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)

        resp = self.images_alt_one.client.get_image_details(
            self.single_member_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image_as_member_updated = resp.entity

        self.assertEqual(
            get_image_as_member_updated, get_image_as_member,
            msg='Unexpected image details received. '
                'Expected: Image details to match '
                'Received: {0} and {1}'.format(get_image_as_member_updated,
                                               get_image_as_member))

        listed_images = self.images_alt_one.behaviors.list_all_images()
        self.assertIn(
            self.single_member_image, listed_images,
            msg='Unexpected images received. Expected: {0} to be present '
                'Received: '
                'Image not present'.format(self.single_member_image))

        resp = self.images.client.list_image_members(
            self.single_member_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        listed_image_members = resp.entity

        self.assertEqual(
            len(listed_image_members), 1,
            msg=('Unexpected number of image members received. Expected: 1 '
                 'Received: {0}').format(len(listed_image_members)))

        [image_member_ids.append(image_member.member_id)
         for image_member in listed_image_members]

        self.assertIn(
            self.alt_one_member_id, image_member_ids,
            msg=('Unexpected image member received. Expected: {0} in list of '
                 'image members '
                 'Received: {1}').format(self.alt_one_member_id,
                                         image_member_ids))

    def test_share_image_with_multiple_members(self):
        """
        @summary: Share image with multiple members

        1) Using alt_one_member, get image details of multiple_members_image,
        which is owned by another user and not shared
        2) Verify that the response code is a 404
        3) Using alt_one_member, list images
        4) Verify that the response is ok
        5) Verify that multiple_members_image is not present
        6) Using alt_two_member, get image details of multiple_members_image,
        which is owned by another user and not shared
        7) Verify that the response code is a 404
        8) Using alt_two_member, list images
        9) Verify that the response is ok
        10) Verify that multiple_members_image is not present
        11) Using image owner, share multiple_members_image with alt_one_member
        12) Verify that the member status is pending
        13) Using alt_one_member, get image details of multiple_members_image
        14) Verify that alt_one_member can now access multiple_members_image
        15) Using alt_one_member, list images
        16) Verify that the response is ok
        17) Verify that multiple_members_image is still not present
        18) Using image owner, share multiple_members_image with alt_two_member
        19) Verify that the member status is pending
        20) Using alt_two_member, get image details of multiple_members_image
        21) Verify that alt_two_member can now access multiple_members_image
        22) Using alt_one_member, list images
        23) Verify that the response is ok
        24) Verify that multiple_members_image is still not present
        25) Using alt_one_member, update image member status to accepted
        26) Using alt_one_member, get image details of multiple_members_image
        27) Verify that the response is ok
        28) Using alt_one_member, list images
        29) Verify that the response is ok
        30) Verify that multiple_members_image is now present
        31) Using alt_two_member, update image member status to accepted
        32) Using alt_two_member, get image details of multiple_members_image
        33) Verify that the response is ok
        34) Using alt_two_member, list images
        35) Verify that the response is ok
        36) Verify that multiple_members_image is now present
        37) List image members of multiple_members_image
        38) Verify that the response is ok
        39) Verify that two image members exist
        40) Verify that both alt_one_member and alt_two_member are present in
        the image members list
        """

        image_member_ids = []

        resp = self.images_alt_one.client.get_image_details(
            self.multiple_members_image.id_)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

        listed_images = self.images_alt_one.behaviors.list_all_images()
        self.assertNotIn(
            self.multiple_members_image, listed_images,
            msg='Unexpected images received. Expected: {0} to not be present '
                'Received: Image present'.format(self.multiple_members_image))

        resp = self.images_alt_two.client.get_image_details(
            self.multiple_members_image.id_)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

        listed_images = self.images_alt_two.behaviors.list_all_images()
        self.assertNotIn(
            self.multiple_members_image, listed_images,
            msg='Unexpected images received. Expected: {0} to not be present '
                'Received: Image present'.format(self.multiple_members_image))

        resp = self.images.client.create_image_member(
            self.multiple_members_image.id_, self.alt_one_member_id)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        member = resp.entity

        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        resp = self.images_alt_one.client.get_image_details(
            self.multiple_members_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_images = self.images_alt_one.behaviors.list_all_images()
        self.assertNotIn(
            self.multiple_members_image, listed_images,
            msg='Unexpected images received. Expected: {0} to not be present '
                'Received: Image present'.format(self.multiple_members_image))

        resp = self.images.client.create_image_member(
            self.multiple_members_image.id_, self.alt_two_member_id)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        member = resp.entity

        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        resp = self.images_alt_two.client.get_image_details(
            self.multiple_members_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_images = self.images_alt_two.behaviors.list_all_images()
        self.assertNotIn(
            self.multiple_members_image, listed_images,
            msg='Unexpected images received. Expected: {0} to not be present '
                'Received: Image present'.format(self.multiple_members_image))

        resp = self.images_alt_one.client.update_image_member(
            self.multiple_members_image.id_, self.alt_one_member_id,
            ImageMemberStatus.ACCEPTED)
        updated_member = resp.entity

        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)

        resp = self.images_alt_one.client.get_image_details(
            self.multiple_members_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_images = self.images_alt_one.behaviors.list_all_images()
        self.assertIn(
            self.multiple_members_image, listed_images,
            msg='Unexpected images received. Expected: {0} to be present '
                'Received: '
                'Image not present'.format(self.multiple_members_image))

        resp = self.images_alt_two.client.update_image_member(
            self.multiple_members_image.id_, self.alt_two_member_id,
            ImageMemberStatus.ACCEPTED)
        updated_member = resp.entity

        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)

        resp = self.images_alt_two.client.get_image_details(
            self.multiple_members_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        listed_images = self.images_alt_two.behaviors.list_all_images()
        self.assertIn(
            self.multiple_members_image, listed_images,
            msg='Unexpected images received. Expected: {0} to be present '
                'Received: '
                'Image not present'.format(self.multiple_members_image))

        resp = self.images.client.list_image_members(
            self.multiple_members_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        listed_image_members = resp.entity

        self.assertEqual(
            len(listed_image_members), 2,
            msg=('Unexpected number of image members received. Expected: 2 '
                 'Received: {0}').format(len(listed_image_members)))

        [image_member_ids.append(image_member.member_id)
         for image_member in listed_image_members]

        self.assertIn(
            self.alt_one_member_id, image_member_ids,
            msg=('Unexpected image member received. Expected: {0} in list of '
                 'image members '
                 'Received: {1}').format(self.alt_one_member_id,
                                         image_member_ids))
        self.assertIn(
            self.alt_two_member_id, image_member_ids,
            msg=('Unexpected image member received. Expected: {0} in list of '
                 'image members '
                 'Received: {1}').format(self.alt_two_member_id,
                                         image_member_ids))

    def test_create_server_from_shared_image(self):
        """
        @summary: Create server from shared image

        1) Using alt_one_member, create active server using imported_image
        2) Verify that the response code is ok
        3) Add the server to resources to be deleted at tear down
        4) Verify that the server has a status of active
        5) Using alt_one_member, get remote instance client for the server
        6) Verify that the user can connect to the server
        """

        resp = self.compute_alt_one_servers_behaviors.create_active_server(
            image_ref=self.imported_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        server = resp.entity

        self.resources.add(
            server.id, self.compute_alt_one_servers_client.delete_server)

        self.assertEqual(
            server.status.lower(), 'active',
            msg=('Unexpected server status received. Expected: active '
                 'Received: {0}').format(server.status.lower()))

        remote_client = (
            self.compute_alt_one_servers_behaviors.get_remote_instance_client(
                server, self.compute.servers.config))
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot connect to server using public ip")

    def test_export_shared_image_as_member_forbidden(self):
        """
        @summary: Export a shared image as member

        1) Using alt_one_member, export no_export_image
        2) Wait for the task to reach failure status
        3) Verify that the export fails
        4) Using alt_one_member, update image member status to accepted
        5) Verify that the response is ok
        6) Using alt_one_member, export no_export_image
        7) Wait for the task to reach failure status
        8) Verify that the export fails
        9) Using alt_one_member, update image member status to rejected
        10) Verify that the response is ok
        11) Using alt_one_member, export no_export_image
        12) Wait for the task to reach failure status
        13) Verify that the export fails
        14) Using alt_one_member, list objects in the container
        15) Verify that the response is ok
        16) Verify that the image does not appear in the container
        """

        input_ = {'image_uuid': self.no_export_image.id_,
                  'receiving_swift_container': self.images.config.export_to}

        resp = self.images_alt_one.client.task_to_export_image(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        task_id = resp.entity.id_

        task = self.images_alt_one.behaviors.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(task.message, Messages.NOT_OWNER_MSG,
                         msg=('Unexpected exception message received. '
                              'Expected: {0}, '
                              'Received: {1}').format(Messages.NOT_OWNER_MSG,
                                                      task.message))

        resp = self.images_alt_one.client.update_image_member(
            self.no_export_image.id_, self.alt_one_member_id,
            ImageMemberStatus.ACCEPTED)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        resp = self.images_alt_one.client.task_to_export_image(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        task_id = resp.entity.id_

        task = self.images_alt_one.behaviors.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(task.message, Messages.NOT_OWNER_MSG,
                         msg=('Unexpected exception message received. '
                              'Expected: {0}, '
                              'Received: {1}').format(Messages.NOT_OWNER_MSG,
                                                      task.message))

        resp = self.images_alt_one.client.update_image_member(
            self.no_export_image.id_, self.alt_one_member_id,
            ImageMemberStatus.REJECTED)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))

        resp = self.images_alt_one.client.task_to_export_image(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        task_id = resp.entity.id_

        task = self.images_alt_one.behaviors.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(task.message, Messages.NOT_OWNER_MSG,
                         msg=('Unexpected exception message received. '
                              'Expected: {0}, '
                              'Received: {1}').format(Messages.NOT_OWNER_MSG,
                                                      task.message))

        resp = self.object_storage_alt_one_client.list_objects(
            self.images.config.export_to)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        objects = resp.entity

        exported_image_names = [obj.name for obj in objects]

        self.assertNotIn('{0}.vhd'.format(self.no_export_image.id_),
                         exported_image_names,
                         msg=('Unexpected images received. '
                              'Expected: No images '
                              'Received: {0}').format(exported_image_names))

    def test_create_snapshot_of_server_created_from_shared_image(self):
        """
        @summary: Create snapshot of server created from shared image

        1) Using alt_one_member, create snapshot of server created from
        snapshot_server
        2) Add the snapshot to resources to be deleted at tear down
        3) Get image details
        4) Verify that the response is ok
        5) Verify that the image's properties are as expected generically
        6) Verify that the image's image type is snapshot
        """

        created_snapshot = (
            self.compute_alt_one_images_behaviors.create_active_image(
                self.snapshot_server.id).entity)

        self.resources.add(
            created_snapshot.id, self.images_alt_one.client.delete_image)

        resp = self.images_alt_one.client.get_image_details(
            created_snapshot.id)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        errors = self.images_alt_one.behaviors.validate_image(get_image)

        if get_image.image_type != ImageType.SNAPSHOT:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_type', ImageType.SNAPSHOT, get_image.image_type))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_export_snapshot_of_server_created_from_shared_image(self):
        """
        @summary: Export snapshot of server created from shared image

        1) Using alt_one_member, create a task to export exported_snapshot
        2) Verify that the response is ok
        3) Wait for the task to reach success status
        4) Using alt_one_member, list objects in the container
        5) Verify that the response is ok
        6) Verify that image was exported successfully
        7) Verify that only one image is returned
        """

        exported_images = []

        input_ = {'image_uuid': self.exported_snapshot.id,
                  'receiving_swift_container': self.images.config.export_to}

        resp = self.images_alt_one.client.task_to_export_image(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        task_id = resp.entity.id_

        self.images_alt_one.behaviors.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        resp = self.object_storage_alt_one_client.list_objects(
            self.images.config.export_to)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        files = resp.entity

        errors, file_names = (
            self.images_alt_one.behaviors.validate_exported_files(
                expect_success=True, files=files,
                image_id=self.exported_snapshot.id))
        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

        exported_images = [
            exported_images.append(name) for name in file_names
            if name == '{0}.vhd'.format(self.exported_snapshot.id)]

        self.assertEqual(
            len(exported_images), 1,
            msg=('Unexpected number of images received. Expected: 1 '
                 'Received: {0}').format(len(exported_images)))
