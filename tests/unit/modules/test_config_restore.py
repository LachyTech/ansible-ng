# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import config_restore
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase


class TestConfigRestoreModule(TestModuleBase):

    module = config_restore

    def setUp(self):
        super(TestConfigRestoreModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.config_restore.ConfigRestoreFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestConfigRestoreModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = {
            'restore': {
                'status': 'completed',
                'restore_log': 'VERSION check passed\nSKU check passed\nrunning restore\nrestore successful\n',
                'exit_code': 0,
                'restore_status': 'import_restore_complete',
            }
        }

    # --- replaced ---
    def test_config_restore_replaced(self):
        set_module_args({
            'config': {
                'config_file': '/tmp/config-backup.cfg',
            },
            'state': 'replaced',
        })

        result = self.execute_module(changed=True)
        self.connection.return_value.send_multipart_request.assert_called_once_with(
            'restore/config',
            file_path='/tmp/config-backup.cfg',
        )

    def test_config_restore_check_mode(self):
        set_module_args({
            '_ansible_check_mode': True,
            'config': {
                'config_file': '/tmp/config-backup.cfg',
            },
            'state': 'replaced',
        })

        result = self.execute_module(changed=True)
        self.connection.return_value.send_multipart_request.assert_not_called()

    def test_config_restore_missing_config_file(self):
        set_module_args({
            'config': {},
            'state': 'replaced',
        })

        self.execute_module(failed=True)

    def test_config_restore_missing_config(self):
        set_module_args({
            'state': 'replaced',
        })

        self.execute_module(failed=True)

    # --- gathered ---
    def test_config_restore_gathered_completed(self):
        set_module_args({
            'state': 'gathered',
        })

        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        self.assertEqual(result['gathered']['restore']['status'], 'completed')
        self.assertEqual(result['gathered']['restore']['exit_code'], 0)
        self.assertIn('restore successful', result['gathered']['restore']['restore_log'])

    def test_config_restore_gathered_in_progress(self):
        def load_in_progress(commands=None):
            self.get_device_data.return_value = {
                'restore': {
                    'status': 'in_progress',
                    'restore_log': '',
                    'exit_code': None,
                    'restore_status': 'system_ready',
                }
            }
        self.load_fixtures = load_in_progress

        set_module_args({
            'state': 'gathered',
        })

        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        self.assertEqual(result['gathered']['restore']['status'], 'in_progress')
        self.assertIsNone(result['gathered']['restore']['exit_code'])

    def test_config_restore_not_changed_on_gathered(self):
        set_module_args({
            'state': 'gathered',
        })

        self.execute_module(changed=False)
