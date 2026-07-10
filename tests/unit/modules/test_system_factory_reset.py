# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
