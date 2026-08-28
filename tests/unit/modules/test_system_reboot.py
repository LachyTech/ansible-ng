# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import system_reboot
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase


class TestSystemRebootModule(TestModuleBase):

    module = system_reboot

    def setUp(self):
        super(TestSystemRebootModule, self).setUp()
        self.maxDiff = None

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestSystemRebootModule, self).tearDown()
        self.mock_connection.stop()

    def test_reboot_issues_post(self):
        set_module_args({})

        commands = [
            {'path': 'system/reboot', 'data': None, 'method': 'POST'}
        ]
        self.execute_module(changed=True, commands=commands)

    def test_check_mode_skips_post(self):
        """In check mode the POST is not sent but changed is still reported"""
        set_module_args({'_ansible_check_mode': True})

        commands = [
            {'path': 'system/reboot', 'data': None, 'method': 'POST'}
        ]
        self.execute_module(changed=True, commands=commands)
        self.connection.return_value.send_request.assert_not_called()
