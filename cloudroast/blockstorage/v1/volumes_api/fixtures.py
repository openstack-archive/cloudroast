from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import memoized

from cloudcafe.common.tools.datagen import random_string
from cloudcafe.blockstorage.v1.volumes_api.config import VolumesAPIConfig
from cloudcafe.blockstorage.v1.volumes_api.client import VolumesClient
from cloudcafe.blockstorage.v1.volumes_api.behaviors import \
    VolumesAPI_Behaviors

from cloudroast.blockstorage.fixtures import \
    BaseBlockstorageTestFixture, BlockstorageAuthComposite


class VolumesComposite(object):

    def __init__(self):
        blockstorage = BlockstorageAuthComposite()
        self.config = VolumesAPIConfig()
        self.client = VolumesClient(
            url=blockstorage.url, auth_token=blockstorage.auth.token,
            tenant_id=blockstorage.auth.tenant_id,
            serialize_format=self.config.serialize_format,
            deserialize_format=self.config.deserialize_format)
        self.behaviors = VolumesAPI_Behaviors(self.client)


class VolumesDatasets():
    """Collection of dataset generators for blockstorage data driven tests"""

    @classmethod
    @memoized
    def volume_types(cls):
        """Returns a DatasetList of Volume Type names and id's"""

        volumes = VolumesComposite()
        resp = volumes.client.list_all_volume_types()
        assert resp.ok, (
            "Unable to retrieve list of volume types during data-driven-test "
            "setup")

        assert resp.entity is not None, (
            "Unable to retrieve list of volume types during data-driven-test "
            "setup: response did not deserialize")

        volume_type_list = resp.entity
        dataset_list = DatasetList()
        for vol_type in volume_type_list:
            data = {'volume_type_name': vol_type.name,
                    'volume_type_id': vol_type.id_}
            dataset_list.append_new_dataset(vol_type.name, data)
        return dataset_list


class VolumesTestFixture(BaseBlockstorageTestFixture):
    """
    @summary: Basic BlockStorage fixture that authenticates and creates a
    volumes api client and behavior object.

    """

    @classmethod
    def setUpClass(cls):
        super(VolumesTestFixture, cls).setUpClass()
        cls.blockstorage = BlockstorageAuthComposite()
        cls.volumes = VolumesComposite()

    @staticmethod
    def random_volume_name():
        return random_string(prefix="Volume_", size=10)

    @staticmethod
    def random_snapshot_name():
        return random_string(prefix="Snapshot_", size=10)

    @classmethod
    def new_volume(cls, size=None, vol_type=None, add_cleanup=True):
        volume = cls.volumes.behaviors.create_available_volume(
            size or cls.volumes.config.min_volume_size,
            vol_type or cls.volumes.config.default_volume_type,
            cls.random_volume_name())

        if add_cleanup:
            cls.addClassCleanup(
                cls.volumes.behaviors.delete_volume_confirmed, volume.id_)

        return volume

    @classmethod
    def new_snapshot(cls, volume_id, add_cleanup=True):
        snapshot = cls.volumes.behaviors.create_available_snapshot(
            volume_id, cls.random_snapshot_name(), force_create=True)

        if add_cleanup:
            cls.addClassCleanup(
                cls.volumes.behaviors.delete_snapshot_confirmed, snapshot.id_)

        return snapshot
