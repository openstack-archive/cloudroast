from cloudcafe.blockstorage.volumes_api.v2.config import VolumesAPIConfig
from cloudcafe.blockstorage.volumes_api.v2.client import VolumesClient
from cloudcafe.blockstorage.volumes_api.v2.behaviors import \
    VolumesAPI_Behaviors
from cloudroast.blockstorage.composites import BlockstorageAuthComposite


class VolumesComposite(object):

    def __init__(self):
        blockstorage = BlockstorageAuthComposite()
        self.config = VolumesAPIConfig()
        self.client = VolumesClient(
            url=blockstorage.url, auth_token=blockstorage.auth.token,
            serialize_format=self.config.serialize_format,
            deserialize_format=self.config.deserialize_format)
        self.behaviors = VolumesAPI_Behaviors(self.client)
