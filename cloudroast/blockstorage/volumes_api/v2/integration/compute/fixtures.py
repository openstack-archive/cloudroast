from cloudcafe.common.tools.datagen import random_string
from cloudcafe.compute.config import ComputeEndpointConfig, MarshallingConfig
from cloudcafe.compute.flavors_api.client import FlavorsClient
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.compute.images_api.client import ImagesClient
from cloudcafe.compute.images_api.config import ImagesConfig
from cloudcafe.compute.images_api.behaviors import ImageBehaviors
from cloudcafe.compute.servers_api.behaviors import ServerBehaviors
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.servers_api.config import ServersConfig
from cloudcafe.compute.volume_attachments_api.client \
    import VolumeAttachmentsAPIClient
from cloudcafe.compute.volume_attachments_api.behaviors \
    import VolumeAttachmentsAPI_Behaviors
from cloudcafe.compute.volume_attachments_api.config \
    import VolumeAttachmentsAPIConfig

from cloudroast.blockstorage.volumes_api.v2.fixtures import VolumesTestFixture
from cloudroast.blockstorage.fixtures import AuthComposite


class ComputeAuthComposite(object):

    def __init__(self):
        self.auth = AuthComposite.authenticate()
        self.endpoint_config = ComputeEndpointConfig()
        self.marshalling_config = MarshallingConfig()

        #Get endpoints from auth data
        self.service = self.auth.access_data.get_service(
            self.endpoint_config.compute_endpoint_name)

        self.servers_url = self.service.get_endpoint(
            self.endpoint_config.region).public_url

        self.client_args = {
            'url': self.servers_url,
            'auth_token': self.auth.access_data.token.id_,
            'serialize_format': self.marshalling_config.serializer,
            'deserialize_format': self.marshalling_config.deserializer}


class ImagesComposite(object):
    def __init__(self):
        compute = ComputeAuthComposite()
        self.config = ImagesConfig()
        self.client = ImagesClient(**compute.client_args)
        self.behaviors = None


class ServersComposite(object):

    def __init__(self):
        compute = ComputeAuthComposite()
        self.config = ServersConfig()
        self.client = ServersClient(**compute.client_args)
        self.behaviors = None


class FlavorsComposite(object):

    def __init__(self):
        compute = ComputeAuthComposite()
        self.config = FlavorsConfig()
        self.client = FlavorsClient(**compute.client_args)
        self.behaviors = None


class VolumeAttachmentsComposite(object):

    def __init__(self):
        compute = ComputeAuthComposite()
        self.config = VolumeAttachmentsAPIConfig()
        self.client = VolumeAttachmentsAPIClient(**compute.client_args)
        self.behaviors = None


class ComputeIntegrationTestFixture(VolumesTestFixture):

    @classmethod
    def setUpClass(cls):
        super(ComputeIntegrationTestFixture, cls).setUpClass()
        cls.compute = ComputeAuthComposite()
        cls.servers = ServersComposite()
        cls.images = ImagesComposite()
        cls.flavors = FlavorsComposite()
        cls.volume_attachments = VolumeAttachmentsComposite()
        cls.servers.behaviors = ServerBehaviors(
            cls.servers.client, cls.servers.config, cls.images.config,
            cls.flavors.config)
        cls.images.behaviors = ImageBehaviors(
            cls.images.client, cls.servers.client, cls.images.config)

        cls.volume_attachments.behaviors = VolumeAttachmentsAPI_Behaviors(
            volume_attachments_client=cls.volume_attachments.client,
            volume_attachments_config=cls.volume_attachments.config,
            volumes_behaviors=cls.volumes.behaviors)

    @staticmethod
    def random_server_name():
        return random_string(prefix="Server_", size=10)

    @classmethod
    def new_server(
            cls, name=None, image=None, flavor=None, add_cleanup=True):

        name = name or cls.random_server_name()
        image = image or cls.images.config.primary_image
        flavor = flavor or cls.flavors.config.primary_flavor
        resp = cls.servers.behaviors.create_active_server(name, image, flavor)

        if add_cleanup:
            cls.addClassCleanup(
                cls.servers.client.delete_server, resp.entity.id)

        return resp.entity


class VolumesImagesIntegrationFixture(ComputeIntegrationTestFixture):

    def calculate_volume_size_for_image(self, image):
        """Get size from image object if possible, or use configured value
        TODO: Move this into a behavior"""

        size = getattr(image, 'min_disk', None)
        if not size:
            # If size is 0 or not reported (None), fallbasck to config minimum
            msg = (
                "Image {image_id} did not report a meaningful disks size. "
                "Falling back to configured min_volume_size_from_image".format(
                    image_id=image.id))
            self.fixture_log.warning(msg)
            size = self.volumes.config.min_volume_from_image_size

        return size

    def create_available_volume_from_img(
            self, volume_type, image, size=None, timeout=None, poll_rate=None):
        """TODO: Move this into a behavior"""

        size = size or self.calculate_volume_size_for_image(image)
        timeout = timeout or self.volumes.config.volume_create_timeout
        poll_rate = \
            poll_rate or self.volumes.config.snapshot_status_poll_frequency

        name = "{0}_{1}".format(
            self.random_volume_name(), str(image.name).replace(" ", "_"))

        resp = self.volumes.client.create_volume(
            size, volume_type.id_, name=name, image_ref=image.id)

        self.assertTrue(
            resp.ok, 'Unable to create volume from image: {0} ({1})'.format(
                image.id, image.name))

        volume = resp.entity
        self.assertIsNotNone(
            volume, 'Unable to deserialize volume create response')
        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, volume.id_)

        self.volumes.behaviors.wait_for_volume_status(
            volume.id_, 'available', timeout, poll_rate=10)

        return volume

    def create_volume_from_image_test(self, volume_type, image):
        size = self.calculate_volume_size_for_image(image)
        volume = self.create_available_volume_from_img(
            volume_type, image, size)

        self.assertEquals(
            str(size), str(volume.size),
            "Expected volume size {0} did not match actual observed volume"
            " size {1}".format(size, volume.size))

            # TODO: Add volume metadata tests to match against image metadata
            # TODO: Add image tests to verify image was correctly built
