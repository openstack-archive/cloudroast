"""
Copyright 2013 Rackspace

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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.identity.fixtures import BaseIdentityAdminTest


class ServicesTest(BaseIdentityAdminTest):

    @classmethod
    def setUpClass(cls):
        super(ServicesTest, cls).setUpClass()
        cls.name = rand_name("service-test-")
        cls.type = rand_name("service-type-")
        cls.description = rand_name("service-desc-")

    @classmethod
    def tearDownClass(cls):
        super(ServicesTest, cls).tearDownClass()

    def test_create_service(self):
        response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        service = response.entity
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.name, service.name)
        self.assertEqual(self.type, service.type_)
        self.assertEqual(self.description, service.description)
        self.assertTrue(service.id_ is not None)

    def test_create_service_by_unauthorized_user(self):
        response = self.demo_tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        self.assertEqual(403, response.status_code)

    def test_create_service_with_request_without_token(self):
        response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description, requestslib_kwargs=self.auth_token)
        self.assertEqual(400, response.status_code)

    def test_create_service_with_empty_name(self):
        """Can create a service with a blank name"""
        response = self.tenant_client.create_service(
            type_=self.type,
            description=self.description)
        self.assertEqual(200, response.status_code)

    def test_create_service_with_duplicate_data(self):
        """Can create two services with the same name,
        type and description
        """
        first_response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        second_response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        self.assertEqual(200, first_response.status_code)
        self.assertEqual(200, second_response.status_code)
        self.assertNotEqual(first_response.entity, second_response.entity)

    def test_list_services(self):
        create_response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(200, create_response.status_code)
        list_services_response = self.tenant_client.list_services()
        services = list_services_response.entity
        self.assertEqual(200, list_services_response.status_code)
        self.assertIn(service, services)

    def test_list_services_by_unauthorized_user(self):
        list_services_response = self.demo_tenant_client.list_services()
        self.assertEqual(403, list_services_response.status_code)

    def test_list_services_with_request_without_token(self):
        list_services_response = self.tenant_client.list_services(
            requestslib_kwargs=self.auth_token)
        self.assertEqual(401, list_services_response.status_code)
        self.assertIn("Could not find token, None.",
                      list_services_response.content)

    def test_delete_service(self):
        create_response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(200, create_response.status_code)
        delete_response = self.tenant_client.delete_service(
            service_id=service.id_)
        self.assertEqual(204, delete_response.status_code)
        self.assertNotIn(service, self.tenant_client.list_services())

    def test_delete_service_by_unauthorized_user(self):
        create_response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(200, create_response.status_code)
        delete_response = self.demo_tenant_client.delete_service(
            service_id=service.id_)
        self.assertEqual(403, delete_response.status_code)

    def test_delete_service_with_request_without_token(self):
        create_response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(200, create_response.status_code)
        delete_response = self.demo_tenant_client.delete_service(
            service_id=service.id_, requestslib_kwargs=self.auth_token)
        self.assertEqual(401, delete_response.status_code)
        self.assertIn("Could not find token, None.", delete_response.content)

    def test_delete_non_existent_service(self):
        funky_service_id = "FUNKY_SERVICE_ID"
        delete_response = self.tenant_client.delete_service(
            service_id=funky_service_id)
        self.assertEqual(404, delete_response.status_code)
        self.assertIn("Could not find service, {0}.".format(funky_service_id),
                      delete_response.content)
