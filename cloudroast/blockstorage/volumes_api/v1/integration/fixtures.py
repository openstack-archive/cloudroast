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

from cloudroast.blockstorage.volumes_api.v1.fixtures import VolumesTestFixture
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
            volumes_client=cls.volumes.client,
            volume_attachments_config=cls.volume_attachments.config,
            volumes_config=cls.volumes.config)

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
