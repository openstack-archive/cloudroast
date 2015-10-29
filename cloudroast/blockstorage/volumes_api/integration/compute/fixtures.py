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

from cloudcafe.common.tools.datagen import random_string
from cloudcafe.compute.composites import ComputeIntegrationComposite
from cloudroast.blockstorage.volumes_api.fixtures import VolumesTestFixture


class ComputeIntegrationTestFixture(VolumesTestFixture):

    @classmethod
    def setUpClass(cls):
        super(ComputeIntegrationTestFixture, cls).setUpClass()
        cls.compute = ComputeIntegrationComposite()
        cls.servers = cls.compute.servers
        cls.flavors = cls.compute.flavors
        cls.images = cls.compute.images
        cls.volume_attachments = cls.compute.volume_attachments

    @classmethod
    def random_server_name(cls):
        return random_string(prefix="Server_", size=10)

    @classmethod
    def new_server(
            cls, name=None, image=None, flavor=None, add_cleanup=True):

        name = name or cls.random_server_name()
        image = image or cls.images.config.primary_image
        flavor = flavor or cls.flavors.config.primary_flavor
        resp = cls.servers.behaviors.create_active_server(
            name, image_ref=image, flavor_ref=flavor)

        if add_cleanup:
            cls.addClassCleanup(
                cls.servers.client.delete_server, resp.entity.id)

        return resp.entity

    @classmethod
    def attach_volume_and_get_device_info(
            cls, server_connection, server_id, volume_id):

        original_details = server_connection.get_all_disk_details()
        attachment = \
            cls.volume_attachments.behaviors.attach_volume_to_server(
                server_id, volume_id)

        assert attachment, "Could not attach volume {0} to server {1}".format(
            volume_id, server_id)

        new_details = server_connection.get_all_disk_details()
        volume_details = [d for d in new_details if d not in original_details]

        cls.fixture_log.debug(volume_details)
        assert len(volume_details) == 1, (
            "Could not uniquely identity the attached volume via the OS.")

        setattr(attachment, 'os_disk_details', volume_details)

        os_disk_device_name = \
            volume_details[0].get('Number') or "/dev/{0}".format(
                volume_details[0].get('name'))

        assert os_disk_device_name, (
            "Could not get a unique device name from the OS")
        setattr(attachment, 'os_disk_device_name', os_disk_device_name)

        return attachment

    @classmethod
    def format_attached_volume(
            cls, server_connection, device_name, fstype=None):
        resp = None
        if device_name.startswith('/dev'):
            resp = server_connection.format_disk(device_name, fstype or 'ext3')
        else:
            resp = server_connection.format_disk(device_name, fstype or 'ntfs')

        assert resp is not None, (
            "An error occured while trying to format the attached volume")

        return resp

    @classmethod
    def mount_attached_volume(
            cls, server_connection, device_name, mount_point=None):
        mount_point = mount_point or server_connection.generate_mountpoint()
        if device_name.startswith('/dev'):
            server_connection.create_directory(mount_point)
        return server_connection.mount_disk(
            source_path=device_name, destination_path=mount_point)

    @classmethod
    def unmount_attached_volume(cls, server_connection, device_name):
        return server_connection.unmount_disk(device_name)

    @classmethod
    def _add_directory_prefix(cls, file_directory_string):
        if not file_directory_string.startswith('/'):
            if len(file_directory_string) == 1:
                file_directory_string = file_directory_string + ":\\"
        return file_directory_string

    @classmethod
    def get_remote_file_md5_hash(
            cls, server_connection, file_directory, file_name):
        file_directory = cls._add_directory_prefix(file_directory)
        return server_connection.get_md5sum_for_remote_file(
            file_directory, file_name)

    @classmethod
    def create_remote_file(
            cls, server_connection, file_directory, file_name,
            file_content=None):

        file_content = file_content or "content"
        file_directory = cls._add_directory_prefix(file_directory)
        return server_connection.create_file(
            file_name, file_content, file_directory)

    @classmethod
    def _get_remote_client(cls, client_type):

        client = None
        if client_type == 'windows':
            from cloudcafe.compute.common.clients.remote_instance.windows.\
                windows_client import WindowsClient
            client = WindowsClient

        if client_type == 'linux':
            from cloudcafe.compute.common.clients.remote_instance.linux.\
                linux_client import LinuxClient
            client = LinuxClient

        if not client:
            raise Exception(
                "Unrecognized client type: {0}".format(client_type))

        return client

    @classmethod
    def _connect(
            cls, remote_client, ip_address=None, username=None,
            connection_timeout=None, key=None, password=None):

        kwargs = {
            'ip_address': ip_address,
            'username': username,
            'connection_timeout': connection_timeout}

        # Key always takes precendence over password if both are provided
        auth_strategy = "key" if key else "password"
        kwargs[auth_strategy] = key or password
        _client = remote_client(**kwargs)
        return _client

    @classmethod
    def connect_to_server(
            cls, ip_address, username='root', password=None, key=None,
            connection_timeout=None, client_type='linux'):
        """Returns a client for communication with the server"""

        remote_client = cls._get_remote_client(client_type)
        return cls._connect(
            remote_client, ip_address=ip_address, username=username,
            connection_timout=connection_timeout, key=key,
            password=password)

    @classmethod
    def get_image_os_type(cls, image_id):
        # TODO: make this method handle the various versions of the images
        # api and image model. This might mean making an images auto composite.

        image = cls.images.client.get_image(image_id).entity
        return image.metadata.get('os_type', '').lower()

    @classmethod
    def connect_to_instance(
            cls, server_instance_model, key=None, connection_timeout=None,
            os_type=None):
        """Special helper method that pulls all neccessary values from a
        compute server model, and returns a client for communication with
        that server
        """

        _usernames = {'windows': 'administrator', 'linux': 'root'}
        ip_address = None
        if hasattr(server_instance_model, 'accessIPv4'):
            ip_address = server_instance_model.accessIPv4
        else:
            ip_address = server_instance_model.addresses.public.ipv4

        if os_type is None:
            os_type = cls.get_image_os_type(server_instance_model.image.id)
        username = _usernames.get(os_type)
        password = server_instance_model.admin_pass
        connection_timeout = \
            connection_timeout or cls.servers.config.connection_timeout
        remote_client = cls._get_remote_client(os_type)

        return cls._connect(
            remote_client, ip_address=ip_address, username=username,
            connection_timeout=connection_timeout, key=key,
            password=password)

    @classmethod
    def setup_server_and_attached_volume_with_data(
            cls, server=None, volume=None):
        """
        Builds a new server using configured defaults
        Attaches, formats and mounts a new volume
        Writes data to the volume
        Saves the md5sum of the written data as a class attribute
        Syncs the filesystem write cache.
        """

        # Build new server using configured defaults
        cls.test_server = server or cls.new_server()

        # Set remote instance client up
        cls.server_conn = cls.connect_to_instance(cls.test_server)
        cls.volume_mount_point = cls.server_conn.generate_mountpoint()
        cls.test_volume = volume or cls.new_volume()

        # Attach Volume
        cls.test_attachment = cls.attach_volume_and_get_device_info(
            cls.server_conn, cls.test_server.id, cls.test_volume.id_)

        # Format Volume
        cls.format_attached_volume(
            cls.server_conn, cls.test_attachment.os_disk_device_name)

        # Mount Volume
        cls.mount_attached_volume(
            cls.server_conn, cls.test_attachment.os_disk_device_name,
            mount_point=cls.volume_mount_point)

        # Write data to volume
        cls.written_data = "a" * 1024
        cls.written_filename = "qe_test_datafile"
        resp = cls.create_remote_file(
            cls.server_conn, cls.volume_mount_point, cls.written_filename,
            file_content=cls.written_data)
        assert resp is not None, (
            "Could not verify writability of attached volume")

        # Save written file md5sum
        cls.original_md5hash = cls.get_remote_file_md5_hash(
            cls.server_conn, cls.volume_mount_point, cls.written_filename)
        assert cls.original_md5hash is not None, (
            "Unable to hash file on mounted volume")

        # Make the fs writes cached data to disk before unmount.
        cls.server_conn.filesystem_sync()

    @classmethod
    def unmount_and_detach_test_volume(cls):
        cls.unmount_attached_volume(
            cls.server_conn, cls.test_attachment.os_disk_device_name)
        cls.volume_attachments.behaviors.delete_volume_attachment(
            cls.test_attachment.id_, cls.test_server.id)

    def calculate_volume_size_for_image(self, image):
        """Get size from image object if possible, or use configured value
        TODO: Move this into a behavior
        """

        size = getattr(image, 'min_disk', None)

        # Log missing sizes
        if not size:
            msg = (
                "Image {image_id} did not report a meaningful disks size. "
                "Falling back to configured min_volume_size_from_image".format(
                    image_id=image.id))
            self.fixture_log.warning(msg)

        # If size is 0 or not reported (None), fall back to configured
        # value for min_volume_size_from_image
        return max(size, self.volumes.config.min_volume_from_image_size)

    def _compare_volume_image_metadata(self, image, volume, key_list=None):
        key_list = key_list or []
        comparable_keys = [
            key for key in image.metadata.keys() if key in key_list]
        error_messages = []
        for key in comparable_keys:
            if key not in volume.volume_image_metadata:
                error_messages.append(
                    "Metadata key '{0}' from image {1} not found in volume"
                    "{2} volume-image-metadata".format(
                        key, image.id, volume.id_))
            elif volume.volume_image_metadata[key] != image.metadata[key]:
                error_messages.append(
                    "Metadata keypair '{0}: {1}' from image {2} did not "
                    "match the keypair '{3}: {4}' in the "
                    "volume-image-metadata of volume {5}".format(
                        key, image.metadata[key], image.id,
                        key, volume.volume_image_metadata[key], volume.id_))
        return error_messages

    def assertImageMetadataWasCopiedToVolume(
            self, image, volume, key_list=None, msg=None):
        errors = self._compare_volume_image_metadata(image, volume, key_list)
        if errors:
            self.fail(self._formatMessage(msg, "\n".join(errors)))

    def assertMinDiskSizeIsSet(self, image, msg=None):
        # TODO: This should probably be an images behavior method that I
        #       wrap here.
        if getattr(image, 'min_disk', 0) <= 0:
            stdmsg = (
                "\nImage {0} '{1}' does not have a min_disk size set, or "
                "has a min_disk size of 0".format(image.id, image.name))
            self.fail(self._formatMessage(msg, stdmsg))

    def check_if_minimum_disk_size_is_set(self, image):
        """Check the image info to make sure the min_disk attribute
        is set"""
        try:
            self.assertMinDiskSizeIsSet(image)
        except AssertionError:
            return False
        return True

    def make_server_snapshot(self, server, add_cleanup=True):
        server_snapshot_name = random_string(
            prefix="cbs_qe_image_of_{0}_".format(server.name), size=10)

        create_img_resp = self.servers.client.create_image(
            server.id, name=server_snapshot_name)

        assert create_img_resp.ok, (
            "Create-Server-Image call failed with a {0}".format(
                create_img_resp.status_code))

        self.images.behaviors.verify_server_snapshotting_progression(server.id)

        # Poll for list of all snapshots and find the one that belongs to our
        # server.
        list_imgs_resp = self.images.client.list_images()
        assert list_imgs_resp.ok, (
            "list-images call failed with a {0}".format(
                list_imgs_resp.status_code))
        assert list_imgs_resp.entity is not None, (
            "Unable to deserialize list-images response".format(
                list_imgs_resp.status_code))
        image_list = list_imgs_resp.entity
        server_snapshot = None
        for img in image_list:
            if img.name == server_snapshot_name:
                server_snapshot = img
                break

        assert server_snapshot is not None, "Could not locate image by name."
        if add_cleanup is True:
            self.addCleanup(
                self.images.client.delete_image, server_snapshot.id)

        # Wait for the image to become active just in case
        self.images.behaviors.wait_for_image_status(
            server_snapshot.id, 'ACTIVE', 10, 600)

        # get the model for the snapshot in question
        resp = self.images.client.get_image(server_snapshot.id)
        assert resp.ok, ("Could not get updated snapshot info after create")
        assert resp.entity is not None, (
            "Could not deserialize snapshot infor response")
        return resp.entity

    def create_bootable_volume_from_server_snapshot(
            self, image, flavor, volume_type):
        # Create a server from the given image and flavor
        server = self.new_server(
            name=None, image=image.id, flavor=flavor.id, add_cleanup=False)
        self.addCleanup(self.servers.client.delete_server, server.id)

        # Make a snapshot of the server via the images api
        server_snapshot = self.make_server_snapshot(server)

        # Create a bootable volume from the server snapshot
        return self.create_volume_from_image_test(volume_type, server_snapshot)

    def create_volume_from_image_test(
            self, volume_type, image, add_cleanup=True):
        size = self.calculate_volume_size_for_image(image)
        volume = self.volumes.behaviors.create_available_volume(
            size, volume_type.id_, image_ref=image.id,
            timeout=self.volumes.config.volume_create_max_timeout)

        if add_cleanup:
            try:
                self.addCleanup(
                    self.volumes.behaviors.delete_volume_confirmed, volume.id_)
            except:
                raise Exception(
                    "Could not create a volume in setup for "
                    "create_volume_from_image test")

        self.assertEquals(
            str(size), str(volume.size),
            "Expected volume size {0} did not match actual observed volume"
            " size {1}".format(size, volume.size))

        # TODO: Break this out into it's own assertion with progress verifer
        # to give the bootable flag time to populate.
        self.assertEquals(
            'true', volume.bootable, "Volume built from image was not marked "
            "as bootable")

        self.assertImageMetadataWasCopiedToVolume(image, volume)

        return volume

    def create_bootable_volume_from_third_snapshot_of_server_test(
            self, image, flavor, volume_type):
        # Create a server from the given image and flavor
        server = self.new_server(
            name=None, image=image.id, flavor=flavor.id, add_cleanup=False)
        self.addCleanup(self.servers.client.delete_server, server.id)

        # Make a snapshot of the server via the images api
        self.make_server_snapshot(server)
        self.servers.behaviors.wait_for_server_status(
            server.id, 'ACTIVE', timeout=300)
        self.make_server_snapshot(server)
        self.servers.behaviors.wait_for_server_status(
            server.id, 'ACTIVE', timeout=300)
        server_snapshot_3 = self.make_server_snapshot(server)
        self.servers.behaviors.wait_for_server_status(
            server.id, 'ACTIVE', timeout=300)

        # Create a bootable volume from the server snapshot
        self.create_volume_from_image_test(volume_type, server_snapshot_3)
