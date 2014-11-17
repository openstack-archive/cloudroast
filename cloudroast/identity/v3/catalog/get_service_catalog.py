from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import tags, DataDrivenClass

from cloudcafe.identity.config import (
    ServiceAdmin, IdentityAdmin, UserAdmin, UserManage, DefaultUser)
from cloudroast.identity.v3.fixture import IdentityV3Fixture


class UserDataset(DatasetList):

    def __init__(self):
        test_cases = [
            {"name": "ServiceAdmin", "data": {
                "get_service_catalog_resp": 200,
                "user_config": ServiceAdmin}},
            {"name": "IdentityAdmin", "data": {
                "get_service_catalog_resp": 200,
                "user_config": IdentityAdmin}},
            {"name": "UserAdmin", "data": {
                "get_service_catalog_resp": 200,
                "user_config": UserAdmin}},
            {"name": "UserManage", "data": {
                "get_service_catalog_resp": 200,
                "user_config": UserManage}},
            {"name": "DefaultUser", "data": {
                "get_service_catalog_resp": 200,
                "user_config": DefaultUser}}]
        for test_case in test_cases:
            self.append_new_dataset(test_case["name"], test_case["data"])


@DataDrivenClass(UserDataset())
class TestCatalog(IdentityV3Fixture):
    """
    @summary Test to verify that the catalog information is retrieved based on
    the user token that is passed in
    """
    get_service_catalog_resp = None
    user_config = None
    catalog_is_empty = False

    @tags('positive', type='regression')
    def test_get_service_catalog(self):
        """ Retrieves the catalog information with all different clients """
        resp = self.v3_composite.apis.catalog.client.get_catalog()
        self.assertEqual(resp.status_code, self.get_service_catalog_resp)

        # Verify the catalog link received is same as the endpoint we target
        self.assertEqual("{0}/auth/catalog".format(
            self.v3_composite.ident_config.global_authentication_endpoint),
            resp.entity.links.self_)

        self._verify_catalog_response(catalog_response=resp,
                                      catalog_is_empty=self.catalog_is_empty)

    @tags('positive', type='regression')
    def test_list_users(self):
        """ This call is blocked and is expected to return 403. """
        resp = self.v3_composite.apis.users.client.list_users()
        self.assertEqual(resp.status_code, 403)
