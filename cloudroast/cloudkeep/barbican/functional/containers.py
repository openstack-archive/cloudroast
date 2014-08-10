"""
Copyright 2014 Rackspace

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

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)

from cafe.drivers.unittest.issue import skip_open_issue
from cloudcafe.cloudkeep.barbican.containers.models.container import SecretRef

from cloudroast.cloudkeep.barbican.fixtures import (
    ContainerFixture, NameDataSetPositive)


class ContainerSizeDataSetPositive(DatasetList):
    def __init__(self):
        self.append_new_dataset('zero', {'num_secrets': 0})
        self.append_new_dataset('one', {'num_secrets': 1})
        self.append_new_dataset('two', {'num_secrets': 2})
        self.append_new_dataset('one_hundred', {'num_secrets': 100})


class EmptyOrNullNamesDataSetPositive(DatasetList):
    """Using these names in a creation request should return the container's
    UUID for the name in the response.
    """
    def __init__(self):
        self.append_new_dataset('null', {'name': None})
        self.append_new_dataset('empty', {'name': ''})
        self.append_new_dataset('space', {'name': ' '})


@DataDrivenFixture
class DataDrivenContainersAPI(ContainerFixture):

    @data_driven_test(dataset_source=ContainerSizeDataSetPositive())
    @tags('positive')
    def ddtest_create_container_of_size(self, num_secrets=None):
        """Covers creating containers of various sizes."""
        # create the given number of secrets
        secret_urls = self.secret_behaviors.create_n_secrets(num_secrets)
        secret_refs = [SecretRef(name='secret{0}'.format(i), ref=url)
                       for i, url in enumerate(secret_urls)]

        # create the container and check the response
        container_resp = self.behaviors.create_container('name', 'generic',
                                                         secret_refs)
        self._check_container_create_response(container_resp)

        # get the container and verify its contents
        get_resp = self.container_client.get_container(container_resp.ref)
        self._check_container_get_resp(get_resp, ref=container_resp.ref,
                                       name='name', type='generic',
                                       num_secrets=num_secrets)

    @data_driven_test(dataset_source=NameDataSetPositive())
    @tags(type='positive')
    def ddtest_create_generic_container_w_name(self, name=None):
        """Covers creating generic containers with various names."""
        container_resp = self.behaviors.create_container(name, 'generic', [])
        self._check_container_create_response(container_resp)

        get_resp = self.container_client.get_container(container_resp.ref)
        self._check_container_get_resp(get_resp, ref=container_resp.ref,
                                       name=name, type='generic')

    @data_driven_test(dataset_source=NameDataSetPositive())
    @tags(type='positive')
    def ddtest_create_rsa_container_w_name(self, name=None):
        """Covers creating rsa containers with various names."""
        secret_urls = self.secret_behaviors.create_n_secrets(3)
        container_resp = self.behaviors.create_rsa_container(
            name, secret_urls[0], secret_urls[1], secret_urls[2])
        self._check_container_create_response(container_resp)

        get_resp = self.container_client.get_container(container_resp.ref)
        self._check_container_get_resp(get_resp, ref=container_resp.ref,
                                       name=name, type='rsa')

    @data_driven_test(dataset_source=NameDataSetPositive())
    @tags(type='positive')
    def ddtest_create_container_w_secret_name(self, name=None):
        """Covers creating containers with various secret names."""
        # create a container with a particular secret name
        responses = self.behaviors.create_container_with_secret(
            name='name', secret_name=name)
        secret_resp, container_resp = responses
        self._check_container_create_response(container_resp)

        # verify the container exists with the expected data
        get_resp = self.container_client.get_container(container_resp.ref)
        self._check_container_get_resp(get_resp, ref=container_resp.ref,
                                       name='name', type='generic',
                                       num_secrets=1)

        # verify the secret's name is returned correctly
        secret_ref = get_resp.entity.secret_refs[0]
        self.assertEqual(secret_ref.name, name)

    @data_driven_test(dataset_source=EmptyOrNullNamesDataSetPositive())
    @tags(type='positive')
    def ddtest_create_generic_container_w_empty_or_null_name(self, name=None):
        """Covers creating a generic container with an empty or null name. The
        returned container should have its UUID as its name.
        """
        container_resp = self.behaviors.create_container(name, 'generic', [])
        self._check_container_create_response(container_resp)

        get_resp = self.container_client.get_container(container_resp.ref)
        self._check_container_get_resp(get_resp, ref=container_resp.ref,
                                       name=container_resp.id, type='generic')


class ContainersAPI(ContainerFixture):

    @tags(type='positive')
    def test_create_container_w_null_secret_name(self):
        """Covers creating a container with None as a secret name."""
        responses = self.behaviors.create_container_with_secret(
            name='name', secret_name=None)
        secret_resp, container_resp = responses
        self._check_container_create_response(container_resp)

        get_resp = self.container_client.get_container(container_resp.ref)
        self._check_container_get_resp(get_resp, ref=container_resp.ref,
                                       name='name', type='generic',
                                       num_secrets=1)

        # verify the secret's name is returned correctly
        secret_ref = get_resp.entity.secret_refs[0]
        self.assertEqual(secret_ref.name, None)

    @tags(type='negative')
    @skip_open_issue('launchpad', '1327438')
    def test_create_container_w_duplicate_secret_refs(self):
        """Covers creating a container with a duplicated secret ref."""

        secret_resp = self.secret_behaviors.create_secret_from_config()
        secret_refs = [SecretRef(name='1', ref=secret_resp.ref),
                       SecretRef(name='2', ref=secret_resp.ref)]

        container_resp = self.behaviors.create_container(
            'name', 'generic', secret_refs)

        self.assertEqual(container_resp.status_code, 400)

    @tags(type='positive')
    def test_create_rsa_container_w_no_passphrase(self):
        """Covers creating an rsa container without a passphrase."""
        secret_urls = self.secret_behaviors.create_n_secrets(2)
        container_resp = self.behaviors.create_rsa_container(
            'name', secret_urls[0], secret_urls[1])
        self._check_container_create_response(container_resp)

        get_resp = self.container_client.get_container(container_resp.ref)
        self._check_container_get_resp(get_resp, ref=container_resp.ref,
                                       name='name', type='rsa')

    @tags(type='negative')
    def test_create_rsa_container_w_invalid_key_names(self):
        """Covers creating an rsa container with three secrets that have the
        wrong names.
        """
        secret_urls = self.secret_behaviors.create_n_secrets(3)
        secret_refs = [SecretRef(name='secret{0}'.format(i), ref=url)
                       for i, url in enumerate(secret_urls)]
        container_resp = self.behaviors.create_container(
            'name', 'rsa', secret_refs)
        self.assertEqual(container_resp.status_code, 400)

    @tags(type='negative')
    def test_create_container_w_order_ref(self):
        """Checks that creating a container with an order ref fails. Containers
        are only allowed to contain references to secrets.
        """
        order_resp = self.order_behaviors.create_order_from_config()
        order_ref = order_resp.ref
        secret_refs = [SecretRef(name='order', ref=order_ref)]
        container_resp = self.behaviors.create_container(
            'name', 'generic', secret_refs)
        self.assertEqual(container_resp.status_code, 404)

    @tags(type='negative')
    def test_create_container_w_invalid_type(self):
        """Container creating should fail with an invalid container type."""
        container_resp = self.behaviors.create_container(
            'name', 'bad_type', [])
        self.assertEqual(container_resp.status_code, 400)

    @tags(type='positive')
    def test_delete_rsa_container(self):
        """Covers deleting an rsa container."""
        secret_urls = self.secret_behaviors.create_n_secrets(3)
        container_resp = self.behaviors.create_rsa_container(
            'name', secret_urls[0], secret_urls[1], secret_urls[2])
        self._check_container_create_response(container_resp)

        # delete container and check the response
        del_resp = self.behaviors.delete_container(container_resp.ref)
        self.assertEqual(del_resp.status_code, 204)

        # check the container is actually deleted
        get_resp = self.container_client.get_container(container_resp.ref)
        self.assertEqual(get_resp.status_code, 404)

    @tags(type='positive')
    def test_delete_generic_container(self):
        """Covers deleting a generic container."""
        container_resp = self.behaviors.create_container('name', 'generic', [])
        self._check_container_create_response(container_resp)

        # delete container and check the response
        del_resp = self.behaviors.delete_container(container_resp.ref)
        self.assertEqual(del_resp.status_code, 204)

        # check the container is actually deleted
        get_resp = self.container_client.get_container(container_resp.ref)
        self.assertEqual(get_resp.status_code, 404)

    @tags(type='negative')
    def test_create_rsa_container_w_no_public_key(self):
        """Creating an rsa container without a public key should fail. RSA
        containers must have at least a public key and private key.
        """
        secret_urls = self.secret_behaviors.create_n_secrets(1)
        secret_refs = [SecretRef(name='public_key', ref=secret_urls[0])]

        container_resp = self.behaviors.create_rsa_container(
            'name', 'rsa', secret_refs)
        self.assertEqual(container_resp.status_code, 400)

    @tags(type='negative')
    def test_create_rsa_container_w_no_private_key(self):
        """Creating an rsa container without a private key should fail. RSA
        containers must have at least a public key and private key.
        """
        secret_urls = self.secret_behaviors.create_n_secrets(1)
        secret_refs = [SecretRef(name='private_key', ref=secret_urls[0])]

        container_resp = self.behaviors.create_rsa_container(
            'name', 'rsa', secret_refs)
        self.assertEqual(container_resp.status_code, 400)

    @tags(type='negative')
    def test_get_nonexistant_container(self):
        """A get on a container that does not exist should return a 404."""
        ref = self.container_client._get_base_url() + '/invalid_uuid'
        get_resp = self.container_client.get_container(ref)
        self.assertEqual(get_resp.status_code, 404)

    @tags(type='negative')
    def test_delete_nonexistant_container(self):
        """A delete on a container that does not exist should return a 404."""
        ref = self.container_client._get_base_url() + '/invalid_uuid'
        del_resp = self.behaviors.delete_container(ref)
        self.assertEqual(del_resp.status_code, 404)
