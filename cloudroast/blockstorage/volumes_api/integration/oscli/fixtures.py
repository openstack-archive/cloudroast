from cloudcafe.common.behaviors import (
    StatusProgressionVerifier, StatusProgressionError)
from cloudcafe.common.tools.datagen import random_string
from cloudcafe.blockstorage.volumes_api.common.models import statuses
from cloudcafe.blockstorage.composites import VolumesAutoComposite
from cloudcafe.compute.composites import ComputeComposite
from cloudcafe.openstackcli.novacli.composites import NovaCLI_Composite
from cloudcafe.openstackcli.cindercli.composites import CinderCLI_Composite

from cloudroast.blockstorage.volumes_api.fixtures import BaseVolumesTestFixture


class CinderCLI_IntegrationFixture(BaseVolumesTestFixture):

    @classmethod
    def setUpClass(cls):
        super(CinderCLI_IntegrationFixture, cls).setUpClass()
        cls.cinder = CinderCLI_Composite()
        cls.volumes = VolumesAutoComposite()


class NovaCLI_IntegrationFixture(BaseVolumesTestFixture):

    @classmethod
    def setUpClass(cls):
        super(NovaCLI_IntegrationFixture, cls).setUpClass()
        cls.nova = NovaCLI_Composite()
        cls.compute = ComputeComposite()
        cls.volumes = VolumesAutoComposite()
        cls.compute.volume_attachments.behaviors = \
            cls.compute.volume_attachments.behavior_class(
                cls.compute.volume_attachments.client,
                cls.compute.volume_attachments.config,
                cls.volumes.client)

    @staticmethod
    def random_string(prefix='NovaClientTestServer_', suffix=None, size=8):
        return random_string(prefix=prefix, suffix=suffix, size=size)

    @classmethod
    def new_volume(cls, size=None, volume_type=None, add_cleanup=True):
        min_size = cls.volumes.behaviors.get_configured_volume_type_property(
            "min_size",
            id_=volume_type or cls.volumes.config.default_volume_type,
            name=volume_type or cls.volumes.config.default_volume_type)
        volume_type = volume_type or cls.volumes.config.default_volume_type
        resp = cls.nova.client.volume_create(
            size or min_size, volume_type=volume_type)
        assert resp.return_code == 0 and resp.entity is not None, (
            "Unable to create volume of size {0} and type {1}".format(
                size, volume_type))
        if add_cleanup:
            cls.addClassCleanup(cls.nova.client.volume_delete, resp.entity.id_)

        return resp.entity

    @classmethod
    def new_server(cls, retry_count=3, print_retries=False, add_cleanup=True):
        # Exztract defaults from configuration
        image = cls.compute.images.config.primary_image
        flavor = cls.compute.flavors.config.primary_flavor

        # Check if image exists
        resp = cls.nova.client.image_show(image)
        assert resp.return_code == 0 and resp.entity is not None, (
            "Unable to verify existance of image {0}.".format(
                image))

        # Check if flavor exists
        resp = cls.nova.client.flavor_show(flavor)
        assert resp.return_code == 0 and resp.entity is not None, (
            "Unable to verify existance of flavor {0}.".format(
                flavor))

        # Build a server
        retries = 0
        last_exception = None
        while retries < retry_count:
            name = cls.random_string()
            print "Attempt {0} to create a server: {1}".format(
                retries + 1, name)
            try:
                resp = cls.nova.client.boot(
                    name, image=image, flavor=flavor, poll=True)
                assert resp.return_code == 0, (
                    'Unable to execute nova boot request successfully.')
                assert resp.entity is not None, (
                    "Unable to create server during setup.  Unable to parse "
                    "nova boot response")

                if add_cleanup:
                    cls.addClassCleanup(
                        cls.nova.client.delete, resp.entity.id_)

                return resp.entity
            except Exception as ex:
                last_exception = ex
                retries += 1
        else:
            raise last_exception

    @classmethod
    def get_volume_status(cls, volume_id):
        return cls.nova.client.volume_show(volume_id).entity.status

    @classmethod
    def verify_volume_availability(cls, volume):
        verifier = StatusProgressionVerifier(
            'volume', volume.id_, cls.get_volume_status, volume.id_)

        verifier.add_state(
            expected_statuses=[statuses.Volume.CREATING],
            acceptable_statuses=[statuses.Volume.AVAILABLE],
            error_statuses=[statuses.Volume.ERROR],
            timeout=1800,
            poll_rate=10)

        verifier.add_state(
            expected_statuses=[
                statuses.Volume.AVAILABLE],
            error_statuses=[
                statuses.Volume.ERROR],
            timeout=1800, poll_rate=10)

        verifier.start()

    def verified_volume_attach(
            self, server_id, volume_id, add_cleanup=True,
            fail_on_progression_error=True):
        # Attach the volume
        attach_response = self.nova.client.volume_attach(server_id, volume_id)

        # Verify that the attach went ok
        assert attach_response.return_code == 0, (
            "nova volume-attach command execution failed with return code {0}"
            .format(attach_response.return_code))
        assert attach_response.entity is not None, (
            "Failed to parse response from nova volume-attach command")
        attachment = attach_response.entity

        # Verify that the volume status doesn't backslide during the attach
        # process, fail if it does instead of erroring out.
        try:
            self.compute.volume_attachments.behaviors.\
                verify_volume_status_progression_during_attachment(volume_id)
        except StatusProgressionError as spe:
            self.fail(str(spe))

        # Verify that the attachment has propagated to all cells
        wait_response = self.compute.volume_attachments.behaviors.\
            wait_for_attachment_to_propagate(
                attachment.id_, self.test_server.id_)
        assert wait_response,  (
            "Unable to verify that attachment propagated toall cells")

        if add_cleanup:
            self.addCleanup(
                self.nova.client.volume_detach, server_id, volume_id)

        return attachment
