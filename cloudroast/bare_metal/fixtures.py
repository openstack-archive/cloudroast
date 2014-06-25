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

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.bare_metal.composites import BareMetalComposite
from cloudcafe.common.resources import ResourcePool


class BareMetalFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        super(BareMetalFixture, cls).setUpClass()
        cls.bare_metal = BareMetalComposite()

        cls.chassis_client = cls.bare_metal.chassis.client
        cls.drivers_client = cls.bare_metal.drivers.client
        cls.nodes_client = cls.bare_metal.nodes.client
        cls.ports_client = cls.bare_metal.ports.client

        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release)

    @classmethod
    def _create_chassis(cls):
        cls.chassis_description = 'test_chassis'
        cls.chassis_extra = {'key1': 'value1'}
        cls.create_chassis_resp = cls.chassis_client.create_chassis(
            description=cls.chassis_description, extra=cls.chassis_extra)
        if cls.create_chassis_resp.ok:
            cls.chassis = cls.create_chassis_resp.entity
            cls.resources.add(cls.chassis.uuid,
                              cls.chassis_client.delete_chassis)
        else:
            cls.assertClassSetupFailure("Unable to create a chassis.")

    @classmethod
    def _create_node(cls):
        cls.node_driver = "fake"
        cls.node_properties = {'property1': 'value1'}
        cls.driver_info = {'info1': 'value2'}
        cls.node_extra = {'meta1': 'value3'}
        cls.create_node_resp = cls.nodes_client.create_node(
            chassis_uuid=cls.chassis.uuid,
            driver=cls.node_driver,
            properties=cls.node_properties,
            driver_info=cls.driver_info,
            extra=cls.node_extra)
        if not cls.create_node_resp.ok:
            cls.assertClassSetupFailure("Unable to create a node.")
        cls.node = cls.create_node_resp.entity
        cls.resources.add(cls.node.uuid,
                          cls.nodes_client.delete_node)

    @classmethod
    def _create_port(cls):
        cls.mac_address = '5d:9a:1f:12:d5:0e'
        cls.port_extra = {'meta1': 'value1'}
        cls.create_port_resp = cls.ports_client.create_port(
            node_uuid=cls.node.uuid,
            address=cls.mac_address,
            extra=cls.port_extra)
        if not cls.create_port_resp.ok:
            cls.assertClassSetupFailure("Unable to create a port.")
        cls.port = cls.create_port_resp.entity
        cls.resources.add(cls.port.uuid,
                          cls.ports_client.delete_port)
