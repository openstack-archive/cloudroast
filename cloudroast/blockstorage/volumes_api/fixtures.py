from cloudcafe.common.tools.datagen import random_string
from cloudcafe.blockstorage.composites import VolumesAutoComposite
from cloudroast.blockstorage.fixtures import BaseBlockstorageTestFixture
from cloudcafe.blockstorage.volumes_api.common.models import statuses
from cloudcafe.common.behaviors import (
    StatusProgressionVerifier, StatusProgressionError)


class BaseVolumesTestFixture(BaseBlockstorageTestFixture):

    @staticmethod
    def random_volume_name():
        return random_string(prefix="Volume_", size=10)

    @staticmethod
    def random_snapshot_name():
        return random_string(prefix="Snapshot_", size=10)


class VolumesTestFixture(BaseVolumesTestFixture):
    """Includes AuthComposite, BlockstorageComposite, and VolumesComposite
    objects
    """

    @classmethod
    def setUpClass(cls):
        super(VolumesTestFixture, cls).setUpClass()
        cls.volumes = VolumesAutoComposite()

    @classmethod
    def new_volume(cls, size=None, vol_type=None, add_cleanup=True):
        """Creates a new volume using configured defaults.
        Uses addClassCleanup to add cleanup after class has finished"""
        min_size = cls.volumes.behaviors.get_configured_volume_type_property(
            "min_size",
            id_=vol_type or cls.volumes.config.default_volume_type,
            name=vol_type or cls.volumes.config.default_volume_type)

        volume = cls.volumes.behaviors.create_available_volume(
            size or min_size,
            vol_type or cls.volumes.config.default_volume_type,
            cls.random_volume_name())

        if add_cleanup:
            cls.addClassCleanup(
                cls.volumes.behaviors.delete_volume_confirmed, volume.id_)

        return volume

    @classmethod
    def new_snapshot(cls, volume_id, add_cleanup=True):
        """Creates a new snapshot using configured defaults.
        Uses addClassCleanup to add cleanup after class has finished"""

        snapshot = cls.volumes.behaviors.create_available_snapshot(
            volume_id, cls.random_snapshot_name(), force_create=True)

        if add_cleanup:
            cls.addClassCleanup(
                cls.volumes.behaviors.delete_snapshot_confirmed, snapshot.id_)

        return snapshot

    def get_volume_response_attributes(self):
        """Returns a list of all expected volume response attributes,
        based on the version of the api under test
        """

        if self.volumes.config.version_under_test == "1":
            from cloudcafe.blockstorage.volumes_api.v1.models.responses import\
                VolumeResponse
            return VolumeResponse.kwarg_map.keys()
        if self.volumes.config.version_under_test == "2":
            from cloudcafe.blockstorage.volumes_api.v2.models.responses import\
                VolumeResponse
            return VolumeResponse.kwarg_map.keys()
        else:
            raise Exception(
                "VolumesAutoConfig cannot be used unless the "
                "'version_under_test' attribute of the VolumesAPIConfig"
                " is set to either '1' or '2'")

    def _compare_volume_metadata(self, volume1, volume2, key_list=None):
        """Compares key-value pairs in the metadata attribute for two
        volumes for every key listed in key_list.
        Returns a list of strings, each string containing information on
        non-matching values."""

        key_list = key_list or []
        comparable_keys = [
            key for key in volume1.metadata.iterkeys() if key in key_list]
        error_messages = []
        for key in comparable_keys:
            if key not in volume2.metadata:
                error_messages.append(
                    "Metadata key '{0}' from volume {1} not found in volume "
                    "{2} metadata".format(key, volume1.id_, volume2.id_))
            elif volume1.metadata[key] != volume2.metadata[key]:
                error_messages.append(
                    "Metadata keypair '{0}: {1}' from volume {2} did not "
                    "match the keypair '{3}: {4}' in volume {5}".format(
                        key, volume1.metadata[key], volume1.id_,
                        key, volume2.metadata[key], volume2.id_))
        return error_messages

    def _compare_volumes(
            self, volume1, volume2, attr_list=None, excluded_attrs_list=None):
        """Compares two volume models by testing if the values for
        volume attribute listed in attr_list match for both volumes.
        Optionally excludes any attributes listed in excluded_attrs_list.
        Returns a list of strings, each string containing information on
        non-matching attributes.
        """

        attr_list = attr_list or self.get_volume_response_attributes()
        excluded_attr_list = excluded_attrs_list or []
        comparable_attrs = [
            attr for attr in attr_list if attr not in excluded_attr_list]

        error_messages = []
        for attr in comparable_attrs:
            attr1 = getattr(volume1, attr, None)
            attr2 = getattr(volume2, attr, None)
            if attr1 != attr2:
                error_messages.append(
                    "\n'{attr}' differs for volumes {v0} and {v1}. ({attr1} "
                    "!= {attr2})".format(
                        attr=attr, v0=volume1.id_, v1=volume2.id_,
                        attr1=attr1, attr2=attr2))

        if 'metadata' in comparable_attrs:
            error_messages.extend(
                self._compare_volume_metadata(volume1, volume2))
        return error_messages

    def verify_volume_suceeded(self, volume_id, volume_size):
        """Raises an exception if the volume doesn't pass through
        the normal expected series of states for a volume create.
        """

        timeout = self.volumes.behaviors.calculate_volume_clone_timeout(
            volume_size)

        verifier = StatusProgressionVerifier(
            'volume', volume_id, self.volumes.behaviors.get_volume_status,
            volume_id)

        verifier.add_state(
            expected_statuses=[statuses.Volume.CREATING],
            acceptable_statuses=[statuses.Volume.AVAILABLE],
            error_statuses=[statuses.Volume.ERROR],
            timeout=self.volumes.config.volume_clone_min_timeout,
            poll_rate=self.volumes.config.volume_status_poll_frequency,
            poll_failure_retry_limit=3)

        verifier.add_state(
            expected_statuses=[statuses.Volume.AVAILABLE],
            error_statuses=[statuses.Volume.ERROR],
            timeout=timeout,
            poll_rate=self.volumes.config.volume_status_poll_frequency,
            poll_failure_retry_limit=3)

        verifier.start()

    def verify_volume_has_errored(self, volume_id):
        """Raises an exception if the volume doesn't enter the "error"
        state, or becomes unexpectedly "available"
        """

        verifier = StatusProgressionVerifier(
            'volume', volume_id, self.volumes.behaviors.get_volume_status,
            volume_id)

        verifier.add_state(
            expected_statuses=[statuses.Volume.ERROR],
            error_statuses=[statuses.Volume.AVAILABLE],
            timeout=self.volumes.config.volume_clone_min_timeout,
            poll_rate=self.volumes.config.volume_status_poll_frequency,
            poll_failure_retry_limit=3)

        verifier.start()

    def assertVolumeAttributesAreEqual(
            self, volume1, volume2, attr_list=None, excluded_attrs_list=None,
            msg=None):
        """An assert wrapper for the _compare_volumes() method"""

        errors = self._compare_volumes(
            volume1, volume2, attr_list, excluded_attrs_list)
        if errors:
            self.fail(self._formatMessage(msg, "\n".join(errors)))

    def assertVolumeMetadataIsEqual(
            self, volume1, volume2, key_list=None, msg=None):
        """An assert wrapper for the _compare_volume_metadata() method"""

        errors = self._compare_volume_metadata(volume1, volume2, key_list)
        if errors:
            self.fail(self._formatMessage(msg, "\n".join(errors)))

    def assertVolumeNotFoundByName(self, volume_name, msg=None):
        """Assert that the volume name provided isn't in a current
        volume list
        """

        if self.volumes.behaviors.find_volume_by_name(volume_name):
            std_msg = (
                "A volume named '{0}' was unexpectedly found in a listing of "
                "all volumes".format(volume_name))
            self.fail(self._formatMessage(msg, std_msg))

    def assertVolumeFoundByName(self, volume_name, msg=None):
        """Assert that the volume name provided is in a current volume list"""

        if not self.volumes.behaviors.find_volume_by_name(volume_name):
            std_msg = (
                "A volume named '{0}' was not found in a listing of all "
                "volumes".format(volume_name))
            self.fail(self._formatMessage(msg, std_msg))

    def assertVolumeNotFoundByID(self, volume_id, msg=None):
        """Assert that the volume id provided isn't in a current volume list"""
        if self.volumes.behaviors.find_volume_by_id(volume_id):
            std_msg = (
                "The volume '{0}' was unexpectedly found in a listing of "
                "all volumes".format(volume_id))
            self.fail(self._formatMessage(msg, std_msg))

    def assertVolumeFoundByID(self, volume_id, msg=None):
        """Assert that the volume id provided is in a current volume list"""
        if not self.volumes.behaviors.find_volume_by_id(volume_id):
            std_msg = (
                "The volume '{0}' was not found in a listing of all "
                "volumes.".format(volume_id))
            self.fail(self._formatMessage(msg, std_msg))

    def assertVolumeCreateSuceeded(self, volume_id, volume_size, msg=None):
        """Assert wrapper for the verify_volume_suceeded() method"""
        try:
            self.verify_volume_suceeded(volume_id, volume_size)
        except Exception as e:
            self.fail(self._formatMessage(msg, str(e)))

    def assertVolumeHasErrored(self, volume_id, msg=None):
        """Assert wrapper for the verify_volume_has_errored() method"""
        try:
            self.verify_volume_has_errored(volume_id)
        except StatusProgressionError as e:
            self.fail(self._formatMessage(msg, str(e)))


class DataDrivenVolumesTestFixture(VolumesTestFixture):
    """Redefines new_volume and new_snapshot to be instance methods so that
    they can use addCleanup by default and cleanup after each test instead
    of after each test suite (The methods defined in VolumesTestFixture
    use addClassCleanup instead, as they are classmethods)"""

    def new_volume(self, size=None, vol_type=None, add_cleanup=True):
        min_size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size",
            id_=vol_type or self.volumes.config.default_volume_type,
            name=vol_type or self.volumes.config.default_volume_type)
        volume = super(DataDrivenVolumesTestFixture, self).new_volume(
            size=size or min_size, vol_type=vol_type, add_cleanup=False)

        if add_cleanup:
            self.addCleanup(
                self.volumes.behaviors.delete_volume_confirmed, volume.id_)

        return volume

    def new_snapshot(self, volume_id, add_cleanup=True):
        snapshot = super(DataDrivenVolumesTestFixture, self).new_snapshot(
            volume_id=volume_id, add_cleanup=False)

        if add_cleanup:
            self.addCleanup(
                self.volumes.behaviors.delete_snapshot_confirmed, snapshot.id_)

        return snapshot
