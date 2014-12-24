from datetime import datetime
from dateutil.parser import parse, tz
from re import match
from time import struct_time
from time import mktime

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (
    tags, DataDrivenClass, data_driven_test)
from cloudcafe.identity.config import IdentityConfig
from cloudcafe.identity.v3.composites import IdentityV3Composite
from cloudcafe.identity.v3.config import (
    ServiceAdmin, IdentityAdmin, UserAdmin, UserManage, DefaultUser)

from cloudroast.identity.v3.fixture import IdentityV3Fixture


class UserDataset(DatasetList):

    def __init__(self):
        test_cases = [
            {"name": "ServiceAdmin", "data": {
                "auth_resp": 201,
                "validate_resp": 200, "user_config": ServiceAdmin}},
            {"name": "IdentityAdmin", "data": {
                "auth_resp": 201,
                "validate_resp": 200, "user_config": IdentityAdmin}},
            {"name": "UserAdmin", "data": {
                "auth_resp": 201,
                "validate_resp": 403, "user_config": UserAdmin}},
            {"name": "UserManage", "data": {
                "auth_resp": 201,
                "validate_resp": 403, "user_config": UserManage}},
            {"name": "DefaultUser", "data": {
                "auth_resp": 201,
                "validate_resp": 403, "user_config": DefaultUser}}]
        for test_case in test_cases:
            self.append_new_dataset(test_case["name"], test_case["data"])


class ValidateDataset(DatasetList):

    def __init__(self):
        test_cases = [
            {"name": "ServiceAdmin", "data": {
                "expected_resp": 200,
                "user_config": ServiceAdmin}},
            {"name": "IdentityAdmin", "data": {
                "expected_resp": 200,
                "user_config": IdentityAdmin}},
            {"name": "UserAdmin", "data": {
                "expected_resp": 403,
                "user_config": UserAdmin}},
            {"name": "UserManage", "data": {
                "expected_resp": 403,
                "user_config": UserManage}},
            {"name": "DefaultUser", "data": {
                "expected_resp": 403,
                "user_config": DefaultUser}}]
        for test_case in test_cases:
            self.append_new_dataset(test_case["name"], test_case["data"])


@DataDrivenClass(UserDataset())
class TestAuthentication(IdentityV3Fixture):
    """
    @summary: Tests to verify authentication of v3 with different combinations
    of username, user id, password, domain and project
    """
    auth_resp = None
    validate_resp = None
    user_config = None
    catalog_is_empty = False

    @classmethod
    def setUpClass(cls):
        """
        Function to create test bed for all the tests. Execute once at the
        beginning of class
        @param cls: instance of class
        """
        super(TestAuthentication, cls).setUpClass()
        cls.v3_composite = IdentityV3Composite(cls.user_config)
        cls.identity_v3 = IdentityConfig()
        cls.to_zone = tz.gettz('America/Chicago')

    @tags('positive', type='regression')
    def test_auth_username_password(self):
        """ Authentication with username and password """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            username=self.v3_composite.user_config.username,
            password=self.v3_composite.user_config.password,)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(resp=resp)

    @tags('positive', type='regression')
    def test_auth_name_password_domain_id(self):
        """
        Authentication with username, password and the domain id of the user
        """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            username=self.v3_composite.user_config.username,
            password=self.v3_composite.user_config.password,
            user_domain_id=self.v3_composite.user_config.domain_id)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(
            resp=resp, user_domain_id=self.v3_composite.user_config.domain_id,
            expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_name_password_domain_name(self):
        """
        Authentication with username, password and the domain name of the user
        """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            username=self.v3_composite.user_config.username,
            password=self.v3_composite.user_config.password,
            user_domain_name=self.v3_composite.user_config.domain_name)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(
            resp=resp,
            user_domain_name=self.v3_composite.user_config.domain_name,
            expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_id_password(self):
        """ Authentication with user id and password """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(resp=resp, expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_id_password_project_id(self):
        """ Authentication with user id, password and the project id """
        resp = self.v3_composite.tokens_client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password,
            project_id=self.v3_composite.user_config.project_id,
            scope=True)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(
            resp=resp, domain_id=self.v3_composite.user_config.project_id,
            expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_id_password_project_name_domain_id(self):
        """
        Authentication with user id, password and the project name, domain id
        in the scope
        """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password,
            project_domain_id=self.v3_composite.user_config.domain_id,
            project_name=self.v3_composite.user_config.project_name,
            scope=True)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(
            resp=resp, domain_id=self.v3_composite.user_config.domain_id,
            expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_id_password_project_name_domain_name(self):
        """
        Authentication with user id, password and the project id, domain id in
        the scope
        """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password,
            project_domain_name=self.v3_composite.user_config.domain_name,
            project_name=self.v3_composite.user_config.project_name,
            scope=True)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(
            resp=resp, domain_name=self.v3_composite.user_config.domain_name,
            expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_id_password_scope_domain_id(self):
        """
        Authentication with user id, password and domain id in the scope
        """
        v3_auth = self.v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password,
            domain_id=self.v3_composite.user_config.domain_id,
            scope=True)
        self.assertEqual(v3_auth.status_code, self.auth_resp)
        self._verify_response(
            resp=v3_auth, domain_id=self.v3_composite.user_config.domain_name,
            expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_id_password_scope_domain_name(self):
        """
        Authentication with user id, password and domain id in the scope
        """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password,
            domain_name=self.v3_composite.user_config.domain_name,
            scope=True)
        self.assertEqual(resp.status_code, self.auth_resp)

        self._verify_response(
            resp=resp, domain_name=self.v3_composite.user_config.domain_name,
            expected_response=self.auth_resp)

    @tags('positive', type='regression')
    def test_auth_with_token(self):
        """
        Authentication with user id and password and authenticate with the
        token received
        """
        resp = self.v3_composite.apis.tokens.client.authenticate(
            user_id=self.v3_composite.user_config.user_id,
            password=self.v3_composite.user_config.password)
        self.assertEqual(resp.status_code, self.auth_resp)

        if self.auth_resp == 201:
            token = resp.headers['x-subject-token']
            token_resp = self.v3_composite.tokens_client.authenticate(
                token_id=token)
            self.assertEqual(token_resp.status_code, 201)

    @data_driven_test(ValidateDataset())
    def ddtest_validate_token(self, user_config=None, expected_resp=None):
        if self.auth_resp == 201:
            validator = IdentityV3Composite(user_config)
            validate_token_resp = validator.apis.tokens.client.validate_token(
                self.v3_composite.token)
            self.assertEqual(validate_token_resp.status_code, expected_resp)

            nocatalog_resp = validator.apis.tokens.client.validate_token(
                self.v3_composite.token, nocatalog="")
            self.assertEqual(nocatalog_resp.status_code, expected_resp)

            if expected_resp == 200:
                for response in [validate_token_resp, nocatalog_resp]:
                    nocatalog = False
                    if response == nocatalog_resp:
                        nocatalog = True
                    self._verify_response(
                        resp=response,
                        domain_id=self.v3_composite.user_config.domain_id,
                        domain_name=self.v3_composite.user_config.domain_name,
                        user_domain_id=self.v3_composite.user_config.domain_id,
                        user_domain_name=(
                            self.v3_composite.user_config.domain_name),
                        expected_response=self.auth_resp, nocatalog=nocatalog)

    def _verify_response(self, resp, user_domain_id=None,
                         user_domain_name=None, domain_id=None,
                         domain_name=None, expected_response=None,
                         nocatalog=False):
        if expected_response == 201:
            token = resp.headers['x-subject-token']
            self.assertIsNotNone(token)

            # Validate token
            if token is not None:
                validate_token = (
                    self.v3_composite.apis.tokens.client.validate_token(
                        token=token))
                self.assertEqual(
                    validate_token.status_code, self.validate_resp)

            # Verify the token contains valid characters
            regex = r'^[\w-]+$'
            valid_token = match(regex, token) is not None
            self.assertTrue(
                valid_token,
                msg=('Token contains invalid chars, returned {0}'.format(
                    valid_token)))

            self.assertIsNotNone(resp.entity.issued_at)

            # Verify the token is valid for about 24hours
            system_time = datetime.now().replace(tzinfo=self.to_zone)
            expires_at = parse(resp.entity.expires_at)

            created_time_tuple = system_time.utctimetuple()
            created_time_in_seconds = mktime(created_time_tuple)

            expiry_time_tuple = expires_at.utctimetuple()
            expiry_time_in_seconds = mktime(expiry_time_tuple)

            delta = (expiry_time_in_seconds - created_time_in_seconds) / 3600
            self.assertTrue(1 <= delta <= 24.1,
                            msg="Token is out of Token Time to live range")

            ptime = parse(resp.entity.expires_at).timetuple()
            self.assertIsInstance(
                ptime, struct_time,
                msg='Token expiration time stamp format is incorrect')

            # Verify user object response
            self.assertIsNotNone(
                resp.entity.user.id_,
                msg='User auth response obj expected user id received '
                    '{0}'.format(resp.entity.user.id_))

            env_parameters = self.identity_v3.environment
            self.assertEqual(resp.entity.user.default_region,
                             env_parameters['region'])

            if user_domain_id is not None:
                self.assertEqual(resp.entity.user.domain.id_, user_domain_id)
            if user_domain_name is not None:
                self.assertEqual(
                    resp.entity.user.domain.name, user_domain_name)

            self.assertEqual(len(resp.entity.extras), 0)

            for method in resp.entity.methods:
                auth_type = "password"
                self.assertEqual(method, auth_type.lower())

            if domain_id is not None:
                self.assertEqual(resp.entity.project.id, domain_id)
                self.assertEqual(resp.entity.project.domain.id_, domain_id)
            if domain_name is not None:
                self.assertEqual(resp.entity.project.name, domain_name)
                self.assertEqual(resp.entity.project.domain.name, domain_name)

            # Roles verification
            role_id_list = []
            for role in resp.entity.roles:
                role_id_list.append(role.id_)
                if role.id_ == self.v3_composite.user_config.role_id:
                    self.assertEqual(
                        self.v3_composite.user_config.role_name, role.name)
                elif role.id_ == self.v3_composite.roles.compute_role_id:
                    self.assertEqual(self.v3_composite.roles.compute_role_name,
                                     role.name)
                    self.assertEqual(self.v3_composite.user_config.domain_id,
                                     role.tenant_id)
                elif role.id_ == self.v3_composite.roles.object_store_role_id:
                    self.assertEqual(
                        self.v3_composite.roles.object_store_role_name,
                        role.name)
                    self.assertEqual(("{0}_{1}".format(
                        self.v3_composite.roles.nast_prefix,
                        self.v3_composite.user_config.domain_id)),
                        role.tenant_id)
                else:
                    role.id_ == self.v3_composite.default_user.role_id

            self.assertIn(self.v3_composite.user_config.role_id, role_id_list)

            if nocatalog:
                self.assertEqual(len(resp.entity.catalog), 0)
                self.catalog_is_empty = True

            # Catalog verification
            self._verify_catalog_response(
                catalog_response=resp, catalog_is_empty=self.catalog_is_empty)
