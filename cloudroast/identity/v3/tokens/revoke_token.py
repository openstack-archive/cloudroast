from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import DataDrivenClass, tags
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.identity.v3.composites import IdentityV3Composite
from cloudcafe.identity.v3.config import (
    ServiceAdmin, IdentityAdmin, UserAdmin, UserManage, DefaultUser)


class ValidateDataset(DatasetList):
    def __init__(self):
        test_cases = [
            {"name": "IdentityAdmin", "data": {
                "auth_exp_resp": 201,
                "not_found_exp_resp": 404,
                "user_config": IdentityAdmin}},
            {"name": "UserAdmin", "data": {
                "auth_exp_resp": 201,
                "not_found_exp_resp": 404,
                "user_config": UserAdmin}},
            {"name": "UserManage", "data": {
                "auth_exp_resp": 201,
                "not_found_exp_resp": 404,
                "user_config": UserManage}},
            {"name": "DefaultUser", "data": {
                "auth_exp_resp": 201,
                "not_found_exp_resp": 404,
                "user_config": DefaultUser}}]
        for test_case in test_cases:
            self.append_new_dataset(test_case["name"], test_case["data"])


@DataDrivenClass(ValidateDataset())
class TestRevokeToken(BaseTestFixture):
    """Test Class for Revoke token"""
    user_config = None

    @classmethod
    def setUpClass(cls):
        """
        Function to create test bed for all the tests. Execute once at the
        beginning of class
        @param cls: instance of class
        """
        super(TestRevokeToken, cls).setUpClass()
        cls.v3_composite = IdentityV3Composite(cls.user_config)

    @tags('positive', type='regression')
    def test_revoke_token(self):
        """ Revoke token """

        resp = self.v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password)
        self.assertEqual(resp.status_code, 201)
        token = resp.headers['x-subject-token']
        self.assertIsNone(resp.entity.audit_ids)

        # Revoke the token
        revoke_toke_resp = self.v3_composite.apis.tokens.client.revoke_token(
            token)
        self.assertEqual(revoke_toke_resp.status_code, 204)

        # Authenticate Service Admin and the other users
        v3_composite = IdentityV3Composite(ServiceAdmin)
        resp = v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password)
        self.assertEqual(resp.status_code, 201)
        token_after_revoke = resp.headers['x-subject-token']
        self.assertIsNotNone(resp.entity.audit_ids)
        self.assertNotEqual(token, token_after_revoke)

        # Validate the previous token should return 404
        validate_token_resp = v3_composite.apis.tokens.client.validate_token(
            token)
        self.assertEqual(validate_token_resp.status_code, 404)
