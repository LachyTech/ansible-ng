# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import config_export
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestConfigExportModule(TestModuleBase):

    module = config_export

    def setUp(self):
        super(TestConfigExportModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.config_export.ConfigExportFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestConfigExportModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("config_export_config.cfg")

    # --- gathered ---
    def test_config_export_gathered(self):
        set_module_args({
            'state': 'gathered',
        })

        result = self.execute_module(changed=False)

        self.assertIn('gathered', result)
        self.assertIsNotNone(result['gathered'])
        self.assertIsInstance(result['gathered'], str)
        self.assertIn('VERSION="25.11.6"', result['gathered'])
        self.assertIn('SKU="CM8148"', result['gathered'])
        # config_export fixture contains physifs
        self.assertIn('physifs', result['gathered'])
        self.assertIn('physifs[0].device="net1"', result['gathered'])
        self.assertIn('physifs[1].device="net2"', result['gathered'])

    def test_config_export_not_changed(self):
        """Config export is read-only and should never report changed"""
        set_module_args({
            'state': 'gathered',
        })

        self.execute_module(changed=False)
