# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import system_factory_reset
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase


class TestSystemFactoryResetModule(TestModuleBase):

    module = system_factory_reset

    def setUp(self):
        super(TestSystemFactoryResetModule, self).setUp()
        self.maxDiff = None

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestSystemFactoryResetModule, self).tearDown()
        self.mock_connection.stop()

    def test_system_factory_reset_issues_delete(self):
        set_module_args({})

        commands = [
            {'path': 'system/config', 'data': None, 'method': 'DELETE'}
        ]
        self.execute_module(changed=True, commands=commands)

    def test_check_mode_skips_delete(self):
        """In check mode the DELETE is not sent but changed is still reported"""
        set_module_args({'_ansible_check_mode': True})

        commands = [
            {'path': 'system/config', 'data': None, 'method': 'DELETE'}
        ]
        self.execute_module(changed=True, commands=commands)
        self.connection.return_value.send_request.assert_not_called()

    # --- warnings ---

    def test_warning_emitted_on_reset(self):
        """A warning is always emitted, including in check mode"""
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'warn') as mock_warn:
            self.execute_module(changed=True)
        mock_warn.assert_called_once()
        self.assertIn('factory defaults', mock_warn.call_args[0][0])

    def test_warning_emitted_in_check_mode(self):
        """Warning is emitted in check mode — it describes what will happen"""
        set_module_args({'_ansible_check_mode': True})

        with patch.object(basic.AnsibleModule, 'warn') as mock_warn:
            self.execute_module(changed=True)
        mock_warn.assert_called_once()
        self.assertIn('factory defaults', mock_warn.call_args[0][0])
