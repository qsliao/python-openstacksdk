# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import mock
import openstack.config as os_client_config

from os_client_config import exceptions as occ_exc

from openstack.cloud import exc
from openstack.cloud import inventory
from openstack.cloud.tests import fakes
from openstack.cloud.tests.unit import base


class TestInventory(base.TestCase):

    def setUp(self):
        super(TestInventory, self).setUp()

    @mock.patch("os_client_config.config.OpenStackConfig")
    @mock.patch("openstack.cloud.OpenStackCloud")
    def test__init(self, mock_cloud, mock_config):
        mock_config.return_value.get_all_clouds.return_value = [{}]

        inv = inventory.OpenStackInventory()

        mock_config.assert_called_once_with(
            config_files=os_client_config.config.CONFIG_FILES
        )
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        self.assertTrue(mock_config.return_value.get_all_clouds.called)

    @mock.patch("os_client_config.config.OpenStackConfig")
    @mock.patch("openstack.cloud.OpenStackCloud")
    def test__init_one_cloud(self, mock_cloud, mock_config):
        mock_config.return_value.get_one_cloud.return_value = [{}]

        inv = inventory.OpenStackInventory(cloud='supercloud')

        mock_config.assert_called_once_with(
            config_files=os_client_config.config.CONFIG_FILES
        )
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        self.assertFalse(mock_config.return_value.get_all_clouds.called)
        mock_config.return_value.get_one_cloud.assert_called_once_with(
            'supercloud')

    @mock.patch("os_client_config.config.OpenStackConfig")
    @mock.patch("openstack.cloud.OpenStackCloud")
    def test__raise_exception_on_no_cloud(self, mock_cloud, mock_config):
        """
        Test that when os-client-config can't find a named cloud, a
        shade exception is emitted.
        """
        mock_config.return_value.get_one_cloud.side_effect = (
            occ_exc.OpenStackConfigException()
        )
        self.assertRaises(exc.OpenStackCloudException,
                          inventory.OpenStackInventory,
                          cloud='supercloud')
        mock_config.return_value.get_one_cloud.assert_called_once_with(
            'supercloud')

    @mock.patch("os_client_config.config.OpenStackConfig")
    @mock.patch("openstack.cloud.OpenStackCloud")
    def test_list_hosts(self, mock_cloud, mock_config):
        mock_config.return_value.get_all_clouds.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = dict(id='server_id', name='server_name')
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]
        inv.clouds[0].get_openstack_vars.return_value = server

        ret = inv.list_hosts()

        inv.clouds[0].list_servers.assert_called_once_with(detailed=True)
        self.assertFalse(inv.clouds[0].get_openstack_vars.called)
        self.assertEqual([server], ret)

    @mock.patch("os_client_config.config.OpenStackConfig")
    @mock.patch("openstack.cloud.OpenStackCloud")
    def test_list_hosts_no_detail(self, mock_cloud, mock_config):
        mock_config.return_value.get_all_clouds.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = self.cloud._normalize_server(
            fakes.make_fake_server(
                '1234', 'test', 'ACTIVE', addresses={}))
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]

        inv.list_hosts(expand=False)

        inv.clouds[0].list_servers.assert_called_once_with(detailed=False)
        self.assertFalse(inv.clouds[0].get_openstack_vars.called)

    @mock.patch("os_client_config.config.OpenStackConfig")
    @mock.patch("openstack.cloud.OpenStackCloud")
    def test_search_hosts(self, mock_cloud, mock_config):
        mock_config.return_value.get_all_clouds.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = dict(id='server_id', name='server_name')
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]
        inv.clouds[0].get_openstack_vars.return_value = server

        ret = inv.search_hosts('server_id')
        self.assertEqual([server], ret)

    @mock.patch("os_client_config.config.OpenStackConfig")
    @mock.patch("openstack.cloud.OpenStackCloud")
    def test_get_host(self, mock_cloud, mock_config):
        mock_config.return_value.get_all_clouds.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = dict(id='server_id', name='server_name')
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]
        inv.clouds[0].get_openstack_vars.return_value = server

        ret = inv.get_host('server_id')
        self.assertEqual(server, ret)