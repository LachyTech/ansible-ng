# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import facts
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase


class TestFactsModule(TestModuleBase):

    module = facts

    def setUp(self):
        super(TestFactsModule, self).setUp()
        self.maxDiff = None

        # Mocks with at least one valid item per module are required to test the facts dispatching
        def _setup_users_mocks(self):
            mock = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.users.UsersFacts.get_device_data"
            )
            mock.start().return_value = [
                {'username': 'user1', 'id': 'users-1', 'enabled': True}
            ]
            return mock

        def _setup_user_authorized_keys_mocks(self):
            mock_users = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.user_authorized_keys.UserAuthorizedKeysFacts.get_users"
            )
            mock_users.start().return_value = [
                {'username': 'user1', 'id': 'users-1', 'enabled': True},
                {'username': 'user2', 'id': 'users-2', 'enabled': True},
            ]
            mock_keys = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.user_authorized_keys.UserAuthorizedKeysFacts.get_device_data"
            )
            mock_keys.start().return_value = [
                {
                    "id": "users_ssh_authorized_keys-1",
                    "key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKoIUqQoc2qsvbCUcs86mwG+zNSJfNJJVJTXXd1VC1Qm user@example2.com",
                    "key_fingerprint": "256 SHA256:LyY9x0V/6FKZRi7eMkEjQ2XNjdkgm9rH+GdBh3IeJ2Q user@example2.com (ED25519)",
                }
            ]
            return mock_users, mock_keys

        def _setup_groups_mocks(self):
            mock = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.groups.GroupsFacts.get_device_data"
            )
            mock.start().return_value = [
                {'groupname': 'admin', 'id': 'groups-1', 'enabled': True}
            ]
            return mock

        def _setup_system_firmware_upgrade_mocks(self):
            mock_version = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.system_firmware_upgrade.SystemFirmwareUpgradeFacts.get_version"
            )
            mock_version.start().return_value = {
                'firmware_version': '25.04.0',
                'rest_api_version': 'v2',
            }

            mock_status = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.system_firmware_upgrade.SystemFirmwareUpgradeFacts.get_upgrade_status"
            )
            mock_status.start().return_value = {'state': 'pending'}

            return mock_version, mock_status

        self.mock_users = _setup_users_mocks(self)
        self.mock_uak_users, self.mock_uak_keys = _setup_user_authorized_keys_mocks(self)
        self.mock_groups = _setup_groups_mocks(self)
        self.mock_fw_version, self.mock_fw_status = _setup_system_firmware_upgrade_mocks(self)

        def _setup_system_info_mocks(self):
            mock = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.system_info.SystemInfoFacts.get_device_data"
            )
            mock.start().return_value = {
                'model_name': 'OM2216-L',
                'serial_number': '22161912071736',
                'has_cellular': True,
                'cellfw_info': {
                    'firmware': {
                        'amss_version': 'SWI9X50C_01.07.02.00',
                        'boot_version': 'SWI9X50C_01.07.02.00',
                        'carrier_id': '4',
                        'config_version': '002.008_004',
                        'model': 'EM7565',
                        'package_id': 'unknown',
                        'sku_id': '1104207',
                    },
                    'operating_mode': {
                        'hw_restricted': 'no',
                        'mode': 'online',
                    },
                },
                'system_versions': {
                    'firmware_version': '23.03.0-dev',
                    'rest_api_version': 'v2',
                },
            }
            return mock

        def _setup_system_diskspace_mocks(self):
            mock = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.system_diskspace.SystemDiskspaceFacts.get_device_data"
            )
            mock.start().return_value = [
                {'mount': '/', 'total': 10240, 'used': 4096, 'free': 6144},
            ]
            return mock

        self.mock_system_info = _setup_system_info_mocks(self)
        self.mock_system_diskspace = _setup_system_diskspace_mocks(self)

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestFactsModule, self).tearDown()
        self.mock_users.stop()
        self.mock_uak_users.stop()
        self.mock_uak_keys.stop()
        self.mock_groups.stop()
        self.mock_fw_version.stop()
        self.mock_fw_status.stop()
        self.mock_system_info.stop()
        self.mock_system_diskspace.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        pass

    def test_facts_gather_users(self):
        """Facts module dispatches correctly to users facts class"""
        set_module_args({'gather_network_resources': ['users']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('ansible_network_resources', result['ansible_facts'])
        self.assertIn('users', result['ansible_facts']['ansible_network_resources'])

    def test_facts_gather_user_authorized_keys(self):
        """Facts module dispatches correctly to user_authorized_keys facts class"""
        set_module_args({'gather_network_resources': ['user_authorized_keys']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('ansible_network_resources', result['ansible_facts'])

    def test_facts_gather_groups(self):
        """Facts module dispatches correctly to groups facts class"""
        set_module_args({'gather_network_resources': ['groups']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('groups', result['ansible_facts']['ansible_network_resources'])

    def test_facts_gather_system_firmware_upgrade(self):
        """Facts module dispatches correctly to system_firmware_upgrade facts class"""
        set_module_args({'gather_network_resources': ['system_firmware_upgrade']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('system_firmware_upgrade', result['ansible_facts']['ansible_network_resources'])

    def test_facts_gather_system_info(self):
        """Facts module dispatches correctly to system_info facts class"""
        set_module_args({'gather_network_resources': ['system_info']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        resources = result['ansible_facts']['ansible_network_resources']
        self.assertIn('system_info', resources)
        self.assertEqual(resources['system_info']['model_name'], 'OM2216-L')
        self.assertEqual(resources['system_info']['serial_number'], '22161912071736')
        self.assertEqual(resources['system_info']['system_versions']['firmware_version'], '23.03.0-dev')

    def test_facts_gather_system_diskspace(self):
        """Facts module dispatches correctly to system_diskspace facts class"""
        set_module_args({'gather_network_resources': ['system_diskspace']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        resources = result['ansible_facts']['ansible_network_resources']
        self.assertIn('system_diskspace', resources)
        self.assertEqual(resources['system_diskspace'][0]['mount'], '/')

    def test_facts_gather_multiple(self):
        """Facts module can gather multiple resources in a single call"""
        set_module_args({'gather_network_resources': ['users', 'groups']})
        result = self.execute_module(changed=False)

        resources = result['ansible_facts']['ansible_network_resources']
        self.assertIn('users', resources)
        self.assertIn('groups', resources)
