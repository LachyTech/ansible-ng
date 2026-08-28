# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils import basic
from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import system_firmware_upgrade
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase


class TestSystemFirmwareUpgradeModule(TestModuleBase):

    module = system_firmware_upgrade

    def setUp(self):
        super(TestSystemFirmwareUpgradeModule, self).setUp()
        self.maxDiff = None

        self.mock_get_version = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.system_firmware_upgrade.SystemFirmwareUpgradeFacts.get_version"
        )
        self.get_version = self.mock_get_version.start()

        self.mock_get_upgrade_status = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.system_firmware_upgrade.SystemFirmwareUpgradeFacts.get_upgrade_status"
        )
        self.get_upgrade_status = self.mock_get_upgrade_status.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestSystemFirmwareUpgradeModule, self).tearDown()
        self.mock_get_version.stop()
        self.mock_get_upgrade_status.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_version.return_value = {
            'firmware_version': '25.04.0',
            'rest_api_version': 'v2',
        }
        self.get_upgrade_status.return_value = {
            'state': 'pending',
        }

    # --- merged: upgrade with file ---
    def test_system_firmware_upgrade_merged_file(self):
        set_module_args({
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/firmware_upgrade',
                'data': {
                    'firmware_file': '/tmp/firmware.raucb',
                    'firmware_options': None,
                },
                'method': 'POST_MULTIPART',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- merged: upgrade with url ---
    def test_system_firmware_upgrade_merged_url(self):
        set_module_args({
            'config': {
                'version': '25.11.0',
                'firmware_image': 'https://ftp.opengear.com/firmware.raucb',
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/firmware_upgrade',
                'data': {
                    'firmware_url': 'https://ftp.opengear.com/firmware.raucb',
                    'firmware_options': None,
                },
                'method': 'POST_MULTIPART',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- merged: idempotent ---
    def test_system_firmware_upgrade_merged_idempotent(self):
        set_module_args({
            'config': {
                'version': '25.04.0',
                'firmware_image': '/tmp/firmware.raucb',
            },
            'state': 'merged',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    # --- merged: with options ---
    def test_system_firmware_upgrade_merged_ignore_version(self):
        set_module_args({
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
                'ignore_version': True,
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/firmware_upgrade',
                'data': {
                    'firmware_file': '/tmp/firmware.raucb',
                    'firmware_options': '-I',
                },
                'method': 'POST_MULTIPART',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_system_firmware_upgrade_merged_erase_config(self):
        set_module_args({
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
                'erase_config': True,
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/firmware_upgrade',
                'data': {
                    'firmware_file': '/tmp/firmware.raucb',
                    'firmware_options': '-E',
                },
                'method': 'POST_MULTIPART',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_system_firmware_upgrade_merged_all_options(self):
        set_module_args({
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
                'ignore_version': True,
                'erase_config': True,
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/firmware_upgrade',
                'data': {
                    'firmware_file': '/tmp/firmware.raucb',
                    'firmware_options': '-I -E',
                },
                'method': 'POST_MULTIPART',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- merged: check mode ---
    def test_system_firmware_upgrade_check_mode(self):
        set_module_args({
            '_ansible_check_mode': True,
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
            },
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_multipart_request.assert_not_called()

    # --- merged: diff mode ---
    def test_system_firmware_upgrade_diff(self):
        set_module_args({
            '_ansible_diff': True,
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
            },
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before['current_version'], '25.04.0')
        self.assertEqual(after['current_version'], '25.11.0')

    def test_system_firmware_upgrade_no_diff_when_idempotent(self):
        set_module_args({
            '_ansible_diff': True,
            'config': {
                'version': '25.04.0',
                'firmware_image': '/tmp/firmware.raucb',
            },
            'state': 'merged',
        })

        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    # --- warnings ---

    def test_erase_config_warning_emitted(self):
        """A warning is emitted when erase_config is set and an upgrade would occur"""
        set_module_args({
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
                'erase_config': True,
            },
            'state': 'merged',
        })

        with patch.object(basic.AnsibleModule, 'warn') as mock_warn:
            self.execute_module(changed=True)
        mock_warn.assert_called_once()
        self.assertIn('erase_config', mock_warn.call_args[0][0])

    def test_erase_config_warning_emitted_in_check_mode(self):
        """Warning is emitted in check mode — it describes what will happen"""
        set_module_args({
            '_ansible_check_mode': True,
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
                'erase_config': True,
            },
            'state': 'merged',
        })

        with patch.object(basic.AnsibleModule, 'warn') as mock_warn:
            self.execute_module(changed=True)
        mock_warn.assert_called_once()
        self.assertIn('erase_config', mock_warn.call_args[0][0])

    def test_no_erase_warning_without_erase_config(self):
        """No erase_config warning is emitted for a regular upgrade"""
        set_module_args({
            'config': {
                'version': '25.11.0',
                'firmware_image': '/tmp/firmware.raucb',
            },
            'state': 'merged',
        })

        with patch.object(basic.AnsibleModule, 'warn') as mock_warn:
            self.execute_module(changed=True)
        mock_warn.assert_not_called()

    def test_no_erase_warning_when_idempotent(self):
        """No erase_config warning is emitted when no upgrade is needed"""
        set_module_args({
            'config': {
                'version': '25.04.0',
                'firmware_image': '/tmp/firmware.raucb',
                'erase_config': True,
            },
            'state': 'merged',
        })

        with patch.object(basic.AnsibleModule, 'warn') as mock_warn:
            self.execute_module(changed=False)
        erase_warnings = [c for c in mock_warn.call_args_list if 'erase_config' in c[0][0]]
        self.assertEqual(erase_warnings, [])

    # --- gathered ---
    def test_system_firmware_upgrade_gathered(self):
        set_module_args({
            'state': 'gathered',
        })

        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        self.assertEqual(result['gathered']['current_version'], '25.04.0')
        self.assertEqual(result['gathered']['upgrade_status']['state'], 'pending')
