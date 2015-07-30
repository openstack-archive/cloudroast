from cafe.drivers.unittest.decorators import \
    tags, data_driven_test, DataDrivenFixture
from cafe.drivers.unittest.datasets import DatasetList
from cloudroast.blockstorage.volumes_api.fixtures import \
    VolumesTestFixture
from cloudcafe.blockstorage.datasets import BlockstorageDatasets


class QuotaTestDatasets(BlockstorageDatasets):

    @classmethod
    def valid_quota_names(cls):

        """Creates a list of expected resource names"""

        quota_test_dataset = DatasetList()

        resources = ["snapshots", "volumes", "gigabytes"]
        vol_types = cls._get_volume_type_names()

        for resource in resources:
            quota_test_dataset.append_new_dataset(
                resource, {"quota_name": resource})

            for vol_name in vol_types:
                resource_key = "{resource}_{vol_name}".format(
                    resource=resource, vol_name=vol_name)
                quota_test_dataset.append_new_dataset(
                    resource_key, {"quota_name": resource_key})

        return quota_test_dataset


@DataDrivenFixture
class QuotaTest(VolumesTestFixture):

    def test_negative_show_default_quota_with_garbage_tenant_id(self):
        """Negative test requesting default quotas with an invalid tenant id"""

        resp = self.volumes.client.get_default_quotas(
            "ivne8vnow4oingsgsdaaaaa__garbage__")
        assert not resp.ok, (
            "test_show_default_quota_with_garbage_tenant_id"
            " passed while using a garbage target tenant_id")

    def test_show_default_quota(self):
        """Test requesting default quotas with a valid id"""

        resp = self.volumes.client.get_default_quotas(
            self.volumes.auth.tenant_id)
        self.assertExactResponseStatus(
            resp, 200, msg="Unexpected response status")

    @data_driven_test(QuotaTestDatasets.valid_quota_names())
    def ddtest_verify_quota(self, quota_name):
        """Test to verify resource key names obtained from response with
        valid_quota_names list
        """

        resp = self.volumes.client.get_default_quotas(
            self.volumes.auth.tenant_id)
        self.assertResponseDeserializedAndOk(resp)
        keylist = vars(resp.entity).keys()
        msg = "Expected quota key {0} not found in default quota list.".format(
            quota_name)
        self.assertIn(quota_name, keylist, msg=msg)
