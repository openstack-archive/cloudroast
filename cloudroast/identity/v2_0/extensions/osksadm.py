from random import randint
import unittest

from cloudroast.identity.v2_0.fixtures import IdentityBaseTestFixture


class BaseOSKSADMApiSmoke(object):
    GET_STATUS_CODE = 200
    CREATE_STATUS_CODE = 200
    UPDATE_STATUS_CODE = 200
    DELETE_STATUS_CODE = 204
    ADD_STATUS_CODE = 200

    def test_get_users(self):
        r = self.client.get_users()
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def test_create_user(self):
        name = "delme{0}".format(randint(1000000, 9000000))
        r = self.client.create_user(
            name=name, enabled=True, email="1@1.com", password="pass")

        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
            self.addCleanup(self.admin_behaviors.delete_user, r.entity.id_)

        self.assertEqual(r.status_code, self.CREATE_STATUS_CODE)

    def test_update_user(self):
        name = "delme{0}".format(randint(1000000, 9000000))
        r = self.client.update_user(
            url_user_id=self.static_user.id_, name=name, enabled=True,
            email="test@updateemail.com", user_id=self.static_user.id_)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.UPDATE_STATUS_CODE)

    def test_delete_user(self):
        user = self.admin_behaviors.create_user()
        r = self.client.delete_user(user.id_)
        if not r.ok:
            self.addCleanup(self.admin_behaviors.delete_user, user.id_)
        self.assertEqual(r.status_code, self.DELETE_STATUS_CODE)

    def test_get_global_roles_for_user(self):
        r = self.client.get_user_global_roles(user_id=self.static_user.id_)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_add_global_role_to_user(self):
        r = self.client.add_global_role_to_user(
            self.static_user.id_, self.static_role.id_)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.ADD_STATUS_CODE)

    @unittest.skip("Global roles not implemented")
    def test_delete_global_role_from_user(self):
        role = self.admin_behaviors.create_role()
        self.addCleanup(self.admin_behaviors.delete_role, role.id_)
        self.admin_behaviors.add_global_role_to_user(
            self.static_user.id_, role.id_)
        r = self.client.delete_global_role_from_user(
            self.static_user.id_, role.id_)
        self.assertEqual(r.status_code, self.DELETE_STATUS_CODE)

    def test_create_tenant(self):
        name = "delme{0}".format(randint(1000000, 9000000))
        r = self.client.create_tenant(name, "test_description", True)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
            self.addCleanup(self.admin_behaviors.delete_tenant, r.entity.id_)
        self.assertEqual(r.status_code, self.CREATE_STATUS_CODE)

    def test_update_tenant(self):
        name = "delme{0}".format(randint(1000000, 9000000))
        r = self.client.update_tenant(
            self.static_tenant.id_, name, "test_description", True,
            self.static_tenant.id_)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.UPDATE_STATUS_CODE)

    def test_delete_tenant(self):
        tenant = self.admin_behaviors.create_tenant()
        r = self.client.delete_tenant(tenant.id_)
        if not r.ok:
            self.addCleanup(self.admin_behaviors.delete_tenant, tenant.id_)
        self.assertEqual(r.status_code, self.DELETE_STATUS_CODE)

    def test_get_users_for_tenant(self):
        r = self.client.get_users_for_tenant(self.identity.tenant_id)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def test_add_role_to_user_for_tenant(self):
        r = self.client.add_role_to_user_for_tenant(
            self.static_tenant.id_, self.static_user.id_, self.static_role.id_)
        self.assertEqual(r.status_code, self.ADD_STATUS_CODE)

    def test_delete_role_from_user_for_tenant(self):
        role = self.admin_behaviors.create_role()
        self.addCleanup(self.admin_behaviors.delete_role, role.id_)
        self.admin_behaviors.add_role_to_user_for_tenant(
            self.static_tenant.id_, self.static_user.id_, role.id_)
        r = self.client.delete_role_from_user_for_tenant(
            self.static_tenant.id_, self.static_user.id_, role.id_)

        self.assertEqual(r.status_code, self.DELETE_STATUS_CODE)

    def test_get_role_by_name(self):
        name = self.static_role.name
        r = self.client.get_role_by_name(name)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def test_create_role(self):
        name = "delme{0}".format(randint(1000000, 9000000))
        r = self.client.create_role(
            role_id=None, name=name, description="description")
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
            self.addCleanup(self.admin_behaviors.delete_role, r.entity.id_)
        self.assertEqual(r.status_code, self.CREATE_STATUS_CODE)

    def test_get_roles(self):
        r = self.client.get_roles()
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def get_role_by_id(self):
        r = self.client.get_role_by_id(self.static_role.id_)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def test_delete_role(self):
        role = self.admin_behaviors.create_role()
        r = self.client.delete_role(role.id_)
        if not r.ok:
            self.addCleanup(self.admin_behaviors.delete_role, role.id_)
        self.assertEqual(r.status_code, self.DELETE_STATUS_CODE)

    def test_get_services(self):
        r = self.client.get_services()
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def test_create_service(self):
        r = self.client.create_service("id112", "name", "type", "description")
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
            self.addCleanup(self.admin_behaviors.delete_service, r.entity.id_)
        self.assertEqual(r.status_code, self.CREATE_STATUS_CODE)

    def test_get_service_by_name(self):
        name = self.static_service.name
        r = self.client.get_service_by_name(name)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def test_get_service_by_id(self):
        r = self.client.get_service_by_id(self.static_service.id_)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")
        self.assertEqual(r.status_code, self.GET_STATUS_CODE)

    def test_delete_service(self):
        service = self.admin_behaviors.create_service()
        r = self.client.delete_service(service.id_)
        if not r.ok:
            self.addCleanup(self.admin_behaviors.delete_service, service.id_)
        self.assertEqual(r.status_code, self.DELETE_STATUS_CODE)


class BaseOSKSADMFixture(IdentityBaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super(BaseOSKSADMFixture, cls).setUpClass()
        cls.admin_behaviors = cls.admin_identity.extensions.osksadm.behaviors

        cls.static_tenant = cls.admin_behaviors.create_tenant()
        cls.addClassCleanup(
            cls.admin_behaviors.delete_tenant, cls.static_tenant.id_)

        cls.static_user = cls.admin_behaviors.create_user(
            tenant_id=cls.static_tenant.id_)
        cls.addClassCleanup(
            cls.admin_behaviors.delete_user, cls.static_user.id_)

        cls.static_role = cls.admin_behaviors.create_role()
        cls.addClassCleanup(
            cls.admin_behaviors.delete_role, cls.static_role.id_)

        cls.static_service = cls.admin_behaviors.create_service()
        cls.addClassCleanup(
            cls.admin_behaviors.delete_service, cls.static_service.id_)


class OSKSADMApiSmoke(BaseOSKSADMFixture, BaseOSKSADMApiSmoke):
    GET_STATUS_CODE = 404
    CREATE_STATUS_CODE = 404
    UPDATE_STATUS_CODE = 404
    DELETE_STATUS_CODE = 404
    ADD_STATUS_CODE = 404

    @classmethod
    def setUpClass(cls):
        super(OSKSADMApiSmoke, cls).setUpClass()
        cls.identity = cls.user_identity
        cls.client = cls.identity.extensions.osksadm.client


class AdminOSKSADMApiSmoke(BaseOSKSADMFixture, BaseOSKSADMApiSmoke):

    @classmethod
    def setUpClass(cls):
        super(AdminOSKSADMApiSmoke, cls).setUpClass()
        cls.identity = cls.admin_identity
        cls.client = cls.identity.extensions.osksadm.client
