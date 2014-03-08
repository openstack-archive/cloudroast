from cloudcafe.common.tools.datagen import random_string
from cloudcafe.blockstorage.composites import VolumesAutoComposite
from cloudroast.blockstorage.fixtures import BaseBlockstorageTestFixture


class VolumesTestFixture(BaseBlockstorageTestFixture):
    """Includes AuthComposite, BlockstorageComposite, and VolumesComposite
    objects
    """

    @classmethod
    def setUpClass(cls):
        super(VolumesTestFixture, cls).setUpClass()
        cls.volumes = VolumesAutoComposite()

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
