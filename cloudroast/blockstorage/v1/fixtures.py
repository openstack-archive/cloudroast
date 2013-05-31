from cafe.common.reporting import cclogging
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import memoized
from cloudcafe.auth.provider import AuthProvider
from cloudroast.blockstorage.fixtures import BaseBlockstorageTestFixture
from cloudcafe.blockstorage.v1.config import BlockStorageConfig
from cloudcafe.blockstorage.v1.volumes_api.config import VolumesAPIConfig
from cloudcafe.blockstorage.v1.volumes_api.client import VolumesClient
from cloudcafe.blockstorage.v1.volumes_api.behaviors import \
    VolumesAPI_Behaviors
from cloudcafe.common.tools.datagen import random_string


class BlockStorage_AuthIntegrationMixin(object):

    @classmethod
    def init_auth_integration(cls):
        cls.auth_token = None
        cls.blockstorage_public_url = None
        cls.tenant_id = None
        cls.blockstorage_config = BlockStorageConfig()
        cls.volumes_api_config = VolumesAPIConfig()

        #Authentication
        auth_provider = AuthProvider()
        access_data = auth_provider.get_access_data()
        if access_data is None:
            cls.assertClassSetupFailure('Authentication failed.')
        _service = access_data.get_service(
            cls.blockstorage_config.identity_service_name)
        _endpoint = _service.get_endpoint(cls.blockstorage_config.region)
        cls.auth_token = access_data.token.id_
        cls.blockstorage_public_url = _endpoint.public_url
        cls.tenant_id = _endpoint.tenant_id

        cls.volumes_client = VolumesClient(
            url=cls.blockstorage_public_url, auth_token=cls.auth_token,
            tenant_id=cls.tenant_id,
            serialize_format=cls.volumes_api_config.serialize_format,
            deserialize_format=cls.volumes_api_config.deserialize_format)
        cls.volumes_behaviors = VolumesAPI_Behaviors(cls.volumes_client)
        cclogging.getLogger('').removeHandler(
            cclogging.setup_new_cchandler(__name__))


class BlockStorageDatasets(BlockStorage_AuthIntegrationMixin):
    """Collection of dataset generators for blockstorage data driven tests"""

    @classmethod
    @memoized
    def volume_types(cls):
        """Returns a DatasetList of Volume Type names and id's"""

        cls.init_auth_integration()
        resp = cls.volumes_client.list_all_volume_types()
        assert resp.ok, (
            "Unable to retrieve list of volume types during  data-driven-test "
            "setup")

        assert resp.entity is not None, (
            "Unable to retrieve list of volume types during  data-driven-test "
            "setup.  Response did not deserialize")

        volume_type_list = resp.entity
        dataset_list = DatasetList()
        for vol_type in volume_type_list:
            data = {'volume_type_name': vol_type.name,
                    'volume_type_id': vol_type.id_}
            dataset_list.append_new_dataset(vol_type.name, data)
        return dataset_list


class BlockStorageTestFixture(
        BaseBlockstorageTestFixture, BlockStorage_AuthIntegrationMixin):
    """
    @summary: Basic BlockStorage fixture that authenticates and creates a
    volumes api client and behavior object.

    """

    @classmethod
    def setUpClass(cls):
        super(BlockStorageTestFixture, cls).setUpClass()
        cls.init_auth_integration()

    @staticmethod
    def random_volume_name():
        return random_string(prefix="Volume_", size=10)

    @staticmethod
    def random_snapshot_name():
        return random_string(prefix="Snapshot_", size=10)

    @classmethod
    def new_volume(cls, size=None, vol_type=None, add_cleanup=True):
        volume = cls.volumes_behaviors.create_available_volume(
            size or cls.volumes_api_config.min_volume_size,
            vol_type or cls.volumes_api_config.default_volume_type,
            cls.random_volume_name())
        cls.addClassCleanup(
            cls.volumes_behaviors.delete_volume_confirmed, volume.id_)
        return volume

    def new_snapshot(self, volume_id):
        return self.volumes_behaviors.create_available_snapshot(
            volume_id, self.random_snapshot_name(), force_create=True)
