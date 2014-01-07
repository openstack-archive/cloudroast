from cafe.drivers.unittest.fixtures import BaseTestFixture
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import memoized

from cloudcafe.common.tools.datagen import random_string
from cloudcafe.openstackcli.cindercli.client import CinderCLI
from cloudcafe.openstackcli.common.config import OpenstackCLI_CommonConfig
from cloudcafe.openstackcli.cindercli.config import CinderCLI_Config
from cloudcafe.openstackcli.cindercli.behaviors import CinderCLI_Behaviors

from cloudroast.blockstorage.volumes_api.v1.fixtures import VolumesComposite


class CinderCLI_Composite(object):

    def __init__(self):
        self.openstack_config = OpenstackCLI_CommonConfig()
        self.config = CinderCLI_Config()
        self._cinder_cli_kwargs = {
            'volume_service_name': self.config.volume_service_name,
            'os_volume_api_version': self.config.os_volume_api_version,
            'os_username': self.openstack_config.os_username,
            'os_password': self.openstack_config.os_password,
            'os_tenant_name': self.openstack_config.os_tenant_name,
            'os_auth_url': self.openstack_config.os_auth_url,
            'os_region_name': self.openstack_config.os_region_name,
            'os_cacert': self.openstack_config.os_cacert,
            'retries': self.openstack_config.retries,
            'debug': self.openstack_config.debug}
        self.client = CinderCLI(**self._cinder_cli_kwargs)
        self.client.set_environment_variables(
            self.config.environment_variable_dictionary)
        self.behaviors = CinderCLI_Behaviors(self.client, self.config)


class CinderVerticalIntegrationComposite(object):
    def __init__(self):
        self.cli = CinderCLI_Composite()
        self.api = VolumesComposite()


class CinderCLI_Datasets():
    """Collection of dataset generators for blockstorage data driven tests"""

    @classmethod
    @memoized
    def volume_types(cls):
        """Returns a DatasetList of Volume Type names and id's"""

        cinder_cli = CinderCLI_Composite()
        volume_type_list = cinder_cli.behaviors.list_volume_types()
        dataset_list = DatasetList()
        for vol_type in volume_type_list:
            data = {'volume_type_name': vol_type.name,
                    'volume_type_id': vol_type.id_}
            dataset_list.append_new_dataset(vol_type.name, data)
        return dataset_list


class CinderTestFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        super(CinderTestFixture, cls).setUpClass()
        cls.cinder = CinderVerticalIntegrationComposite()

    @staticmethod
    def random_volume_name():
        return random_string(prefix="Volume_", size=10)

    @staticmethod
    def random_snapshot_name():
        return random_string(prefix="Snapshot_", size=10)
