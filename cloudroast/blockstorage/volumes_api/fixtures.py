"""
Copyright 2015 Rackspace

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
    """
    Sets up resources required for non-integration volumes testing
    """

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        Presents an instance of the
        :class:`cloudcafe.blockstorage.composites.VolumesAutoComposite` class.
        """

        super(VolumesTestFixture, cls).setUpClass()
        cls.volumes = VolumesAutoComposite()

    @classmethod
    def new_volume(cls, size=None, vol_type=None, add_cleanup=True):
        """
        Creates a new volume using configured defaults.

        :param size: How large in GB to make the volume.
        :param vol_type: Either the name or id of the type of volume requsted.
        :add_cleanup: If True, deletes the volume after classTearDown.
        """

        min_size = cls.volumes.behaviors.get_configured_volume_type_property(
            "min_size",
            id_=vol_type or cls.volumes.config.default_volume_type,
            name=vol_type or cls.volumes.config.default_volume_type)

        volume = cls.volumes.behaviors.create_available_volume(
            size or min_size,
            vol_type or cls.volumes.config.default_volume_type,
            cls.random_volume_name())

        if add_cleanup:
            cls.add_cleanup(
                cls, cls.volumes.behaviors.delete_volume_confirmed, volume.id_)

        return volume

    @classmethod
    def new_snapshot(cls, volume_id, add_cleanup=True):
        """
        Creates a new volume snapshot using configured defaults.

        :param volume_id: The id of volume to make a snapshot from.
        :add_cleanup: If True, deletes the volume after classTearDown.
        """

        snapshot = cls.volumes.behaviors.create_available_snapshot(
            volume_id, cls.random_snapshot_name(), force_create=True)

        if add_cleanup:
            cls.add_cleanup(
                cls, cls.volumes.behaviors.delete_snapshot_confirmed,
                snapshot.id_)

        return snapshot

    def get_volume_response_attributes(self):
        """
        Generated expected volume response fields, based on the api version.

        Uses volumes.config.version_under_test to decide what fields are
        applicable.

        :returns: list -- response fields
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

    # Volume comparison methods and method assertion wrappers

    def _compare_volume_metadata(self, volume1, volume2, key_list=None):
        """Compares key-value pairs in the metadata attribute for two
        volumes for every key listed in key_list.

        :param volume1: id of the first volume to compare
        :param volume2: id of the second volume to compare
        :param key_list: whitelist of keys that should be compared between
                         volume1 and volume2
        :returns: list - strings, each string containing information on
                  non-matching values (error messages).
        """

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

        :param volume1: id of the first volume to compare
        :param volume2: id of the second volume to compare
        :param attr_list: whitelist of keys that should be compared between
                         volume1 and volume2
        :param excluded_attrs_list: blacklist of keys that should not be
                         compared between volume1 and volume2
        :returns: list - strings, each string containing information on
                  non-matching attributes (error messages).
        """

        attr_list = attr_list or self.get_volume_response_attributes()
        excluded_attr_list = excluded_attrs_list or []
        comparable_attrs = [
            attr for attr in attr_list if attr not in excluded_attr_list]

        error_messages = []
        for attr in comparable_attrs:
            in_vol1 = hasattr(volume1, attr)
            in_vol2 = hasattr(volume2, attr)
            if in_vol1 and in_vol2:
                attr1 = getattr(volume1, attr, None)
                attr2 = getattr(volume2, attr, None)
                if attr1 != attr2:
                    error_messages.append(
                        "\n'{attr}' differs for volumes {v0} and {v1}. "
                        "({attr1} != {attr2})".format(
                            attr=attr, v0=volume1.id_, v1=volume2.id_,
                            attr1=attr1, attr2=attr2))
            else:
                if not in_vol1 and in_vol2:
                    error_messages.append(
                        "\n'{attr}' is present in {v0} but not in {v1}."
                        .format(attr=attr, v0=volume1.id_, v1=volume2.id_))
                elif in_vol1 and not in_vol2:
                    error_messages.append(
                        "\n'{attr}' is present in {v1} but not in {v0}."
                        .format(attr=attr, v0=volume1.id_, v1=volume2.id_))
                elif not in_vol1 and not in_vol2:
                    error_messages.append(
                        "\n'{attr}' is not present in {v0} or {v1}, "
                        "but is expected to be.".format(
                            attr=attr, v0=volume1.id_, v1=volume2.id_))

        if 'metadata' in comparable_attrs:
            error_messages.extend(
                self._compare_volume_metadata(volume1, volume2))
        return error_messages

    def assertVolumeAttributesAreEqual(
            self, volume1, volume2, attr_list=None, excluded_attrs_list=None,
            msg=None):
        """
        An assert wrapper for the _compare_volumes() method
        """

        errors = self._compare_volumes(
            volume1, volume2, attr_list, excluded_attrs_list)
        if errors:
            self.fail(self._formatMessage(msg, "\n".join(errors)))

    def assertVolumeMetadataIsEqual(
            self, volume1, volume2, key_list=None, msg=None):
        """
        An assert wrapper for the _compare_volume_metadata() method
        """

        errors = self._compare_volume_metadata(volume1, volume2, key_list)
        if errors:
            self.fail(self._formatMessage(msg, "\n".join(errors)))

    # Volume search assertion wrappers

    def assertVolumeNotFoundByName(self, volume_name, msg=None):
        """
        Assert that the volume name provided is not in the current volume list
        """

        if self.volumes.behaviors.find_volume_by_name(volume_name):
            std_msg = (
                "A volume named '{0}' was unexpectedly found in a listing of "
                "all volumes".format(volume_name))
            self.fail(self._formatMessage(msg, std_msg))

    def assertVolumeFoundByName(self, volume_name, msg=None):
        """
        Assert that the volume name provided is in the current volume list
        """

        if not self.volumes.behaviors.find_volume_by_name(volume_name):
            std_msg = (
                "A volume named '{0}' was not found in a listing of all "
                "volumes".format(volume_name))
            self.fail(self._formatMessage(msg, std_msg))

    def assertVolumeNotFoundByID(self, volume_id, msg=None):
        """
        Assert that the volume id provided is not in the current volume list
        """

        if self.volumes.behaviors.find_volume_by_id(volume_id):
            std_msg = (
                "The volume '{0}' was unexpectedly found in a listing of "
                "all volumes".format(volume_id))
            self.fail(self._formatMessage(msg, std_msg))

    def assertVolumeFoundByID(self, volume_id, msg=None):
        """
        Assert that the volume id provided is in a current volume list
        """

        if not self.volumes.behaviors.find_volume_by_id(volume_id):
            std_msg = (
                "The volume '{0}' was not found in a listing of all "
                "volumes.".format(volume_id))
            self.fail(self._formatMessage(msg, std_msg))

    # Volume build sucess and failure methods and method assertion wrappers

    def verify_volume_build_suceeded(self, volume_id, timeout):
        """
        Raises an exception if the volume does not pass through the normal
        expected series of states for a volume create.
        """

        self.volumes.behaviors.verify_volume_create_status_progresion(
            volume_id, timeout)

    def verify_volume_build_has_errored(self, volume_id, timeout):
        """
        Raises an exception if the volume does not enter the "error" state,
        or becomes unexpectedly "available"
        """

        verifier = StatusProgressionVerifier(
            'volume', volume_id, self.volumes.behaviors.get_volume_status,
            volume_id)

        # Every known status that isn't 'ERROR' is added to the error statuses
        error_statuses = statuses.Volume.values()
        error_statuses.remove(statuses.Volume.ERROR)
        error_statuses.remove(statuses.Volume.CREATING)
        verifier.add_state(
            expected_statuses=[statuses.Volume.ERROR],
            error_statuses=error_statuses,
            timeout=timeout,
            poll_rate=self.volumes.config.volume_status_poll_frequency,
            poll_failure_retry_limit=3)
        verifier.start()

    # Snapshot build success and failure methods

    def verify_snapshot_build_succeeded(self, snapshot_id, timeout):
        """
        Raises an exception if the snapshot does not pass through the normal
        expected series of states for a snapshot create.
        """

        self.volumes.behaviors.verify_snapshot_create_status_progression(
            snapshot_id, timeout)

    def verify_snapshot_build_has_errored(self, snapshot_id, timeout):
        """
        Raises an exception if the snapshot does not enter the "error" state,
        or becomes unexpectedly "available"
        """

        verifier = StatusProgressionVerifier(
            'snapshot', snapshot_id,
            self.volumes.behaviors.get_snapshot_status, snapshot_id)

        # Every known status that isn't 'ERROR' is added to the error statuses
        error_statuses = statuses.Snapshot.values()
        error_statuses.remove(statuses.Snapshot.ERROR)
        error_statuses.remove(statuses.Snapshot.CREATING)
        verifier.add_state(
            expected_statuses=[statuses.Snapshot.ERROR],
            error_statuses=error_statuses,
            timeout=timeout,
            poll_rate=self.volumes.config.snapshot_status_poll_frequency,
            poll_failure_retry_limit=3)
        verifier.start()

    def _assertVolumeBuildSucceededWithTimeout(
            self, volume_id, timeout, msg=None):
        """
        Assert wrapper for the verify_volume_build_suceeded() method
        """

        try:
            self.verify_volume_build_suceeded(volume_id, timeout)
        except StatusProgressionError as e:
            self.fail(self._formatMessage(msg, str(e)))

    def _assertVolumeBuildErroredWithTimeout(
            self, volume_id, timeout, msg=None):
        """
        Assert wrapper for the verify_volume_has_errored() method
        """

        try:
            self.verify_volume_build_has_errored(volume_id, timeout)
        except StatusProgressionError as e:
            self.fail(self._formatMessage(msg, str(e)))

    def _assertSnapshotBuildSucceededWithTimeout(
            self, snapshot_id, timeout, msg=None):
        """
        Assert wrapper for the verify_snapshot_build_succeeded() method
        """

        try:
            self.verify_snapshot_build_succeeded(snapshot_id, timeout)
        except StatusProgressionError as e:
            self.fail(self._formatMessage(msg, str(e)))

    def _assertSnapshotBuildErroredWithTimeout(
            self, snapshot_id, timeout, msg=None):
        """
        Assert wrapper for the verify_snapshot_build_has_errored() method
        """

        try:
            self.verify_snapshot_build_has_errored(snapshot_id, timeout)
        except StatusProgressionError as e:
            self.fail(self._formatMessage(msg, str(e)))

    def assertVolumeCreateSucceeded(self, volume_id, volume_size, msg=None):
        """
        Assert that a no-source volume create suceeded
        """

        timeout = self.volumes.behaviors.calculate_volume_create_timeout(
            volume_size)
        self._assertVolumeBuildSucceededWithTimeout(
            volume_id, timeout, msg=msg)

    def assertVolumeCreateErrored(self, volume_id, volume_size, msg=None):
        """
        Assert that a no-source volume create errored
        """

        timeout = self.volumes.behaviors.calculate_volume_create_timeout(
            volume_size)
        self._assertVolumeBuildErroredWithTimeout(volume_id, timeout, msg=msg)

    def assertVolumeCloneSucceeded(self, volume_id, volume_size, msg=None):
        """
        Assert that a volume created from another volume has suceeded
        """

        timeout = self.volumes.behaviors.calculate_volume_clone_timeout(
            volume_size)
        self._assertVolumeBuildSucceededWithTimeout(
            volume_id, timeout, msg=msg)

    def assertVolumeCloneErrored(self, volume_id, volume_size, msg=None):
        """
        Assert that a volume created from another volume has errored
        """

        timeout = self.volumes.behaviors.calculate_volume_clone_timeout(
            volume_size)
        self._assertVolumeBuildErroredWithTimeout(volume_id, timeout, msg=msg)

    def assertImageToVolumeCopySucceeded(
            self, volume_id, volume_size, msg=None):
        """
        Assert that a volume created from an image has suceeded
        """

        timeout = (
            self.volumes.behaviors.calculate_copy_image_to_volume_timeout(
                volume_size))
        self._assertVolumeBuildSucceededWithTimeout(
            volume_id, timeout, msg=msg)

    def assertImageToVolumeCopyErrored(
            self, volume_id, volume_size, msg=None):
        """
        Assert that a volume created from an image has errored
        """

        timeout = (
            self.volumes.behaviors.calculate_copy_image_to_volume_timeout(
                volume_size))
        self._assertVolumeBuildErroredWithTimeout(volume_id, timeout, msg=msg)

    def assertRestoreSnapshotToVolumeSucceeded(
            self, volume_id, volume_size, msg=None):
        """
        Assert that a volume created from a volume snapshot has suceeded
        """

        timeout = self.volumes.behaviors.calculate_snapshot_restore_timeout(
            volume_size)
        self._assertVolumeBuildSucceededWithTimeout(
            volume_id, timeout, msg=msg)

    def assertRestoreSnapshotToVolumeErrored(
            self, volume_id, volume_size, msg=None):
        """
        Assert that a volume created from a volume snapshot has errored
        """

        timeout = self.volumes.behaviors.calculate_snapshot_restore_timeout(
            volume_size)
        self._assertVolumeBuildErroredWithTimeout(volume_id, timeout, msg=msg)

    def assertSnapshotCreateSucceeded(
            self, snapshot_id, volume_size, msg=None):
        """
        Assert that a snapshot created from a volume has succeeded
        """

        timeout = self.volumes.behaviors.calculate_snapshot_restore_timeout(
            volume_size)
        self._assertSnapshotBuildSucceededWithTimeout(
            snapshot_id, timeout, msg=msg)

    def assertSnapshotCreateErrored(
            self, snapshot_id, volume_size, msg=None):
        """
        Assert that a snapshot created from a volume has errored
        """

        timeout = self.volumes.behaviors.calculate_snapshot_restore_timeout(
            volume_size)
        self._assertSnapshotBuildErroredWithTimeout(
            snapshot_id, timeout, msg=msg)
