from cloudcafe.compute.config import ComputeEndpointConfig, MarshallingConfig
from cloudcafe.compute.flavors_api.client import FlavorsClient
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.compute.images_api.client import ImagesClient
from cloudcafe.compute.images_api.config import ImagesConfig
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.servers_api.config import ServersConfig
from cloudcafe.compute.images_api.behaviors import ImageBehaviors
from cloudcafe.compute.servers_api.behaviors import ServerBehaviors
from cloudcafe.compute.volume_attachments_api.client \
    import VolumeAttachmentsAPIClient
from cloudcafe.compute.volume_attachments_api.config \
    import VolumeAttachmentsAPIConfig
from cloudcafe.compute.volume_attachments_api.behaviors \
    import VolumeAttachmentsAPI_Behaviors

from cloudroast.blockstorage.composites import AuthComposite


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
    behavior_class = ImageBehaviors

    def __init__(self):
        compute = ComputeAuthComposite()
        self.config = ImagesConfig()
        self.client = ImagesClient(**compute.client_args)
        self.behaviors = None


class ServersComposite(object):
    behavior_class = ServerBehaviors

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
    behavior_class = VolumeAttachmentsAPI_Behaviors

    def __init__(self):
        compute = ComputeAuthComposite()
        self.config = VolumeAttachmentsAPIConfig()
        self.client = VolumeAttachmentsAPIClient(**compute.client_args)
        self.behaviors = None
