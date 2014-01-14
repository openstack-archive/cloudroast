from cafe.drivers.unittest.decorators import memoized

from cloudcafe.auth.provider import AuthProvider
from cloudcafe.blockstorage.config import BlockStorageConfig


class AuthComposite(object):

    @classmethod
    @memoized
    def authenticate(cls):
        """ Should only be called from an instance of AuthComposite """
        access_data = AuthProvider.get_access_data()
        if access_data is None:
            raise AssertionError('Authentication failed in setup')
        return AuthComposite(access_data)

    def __init__(self, access_data):
        self.access_data = access_data
        self.token = self.access_data.token.id_
        self.tenant_id = self.access_data.token.tenant.id_


class BlockstorageAuthComposite(object):

    def __init__(self):
        self.auth = AuthComposite.authenticate()
        self.config = BlockStorageConfig()

        self.service = self.auth.access_data.get_service(
            self.config.identity_service_name)
        self.endpoint = self.service.get_endpoint(self.config.region)
        self.url = self.endpoint.public_url
