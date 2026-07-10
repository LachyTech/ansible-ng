# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import system_time
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestSystemTimeModule(TestModuleBase):

    module = system_time

    def setUp(self):
        super(TestSystemTimeModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.system_time.SystemTimeFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestSystemTimeModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("system_time_config.cfg")

    # --- timezone (idempotent) ---
    def test_timezone_change(self):
        set_module_args({
            'config': {'timezone': 'Etc/UTC'},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/timezone',
                'data': {'system_timezone': {'timezone': 'Etc/UTC'}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_timezone_idempotent(self):
        set_module_args({
            'config': {'timezone': 'Australia/Brisbane'},
            'state': 'merged',
        })

        self.execute_module(changed=False, commands=[])

    # --- time (non-idempotent, write-only) ---
    def test_time_always_pushed_when_provided(self):
        set_module_args({
            'config': {'time': '2026-07-08T09:30:00Z'},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/time',
                'data': {'time': {'time': '2026-07-08T09:30:00Z'}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- gathered excludes the momentary clock by default ---
    def test_gathered_excludes_time(self):
        set_module_args({'state': 'gathered'})

        result = self.execute_module(changed=False)

        gathered = result['gathered']
        self.assertEqual(gathered['timezone'], 'Australia/Brisbane')
        self.assertNotIn('time', gathered)

    def test_gathered_includes_time_when_requested(self):
        set_module_args({'state': 'gathered', 'gather_time': True})

        result = self.execute_module(changed=False)

        gathered = result['gathered']
        self.assertEqual(gathered['timezone'], 'Australia/Brisbane')
        self.assertEqual(gathered['time'], '2026-07-08T00:00:00Z')

    def test_time_never_in_diff_even_with_gather_time(self):
        """gather_time only affects `gathered`; it must not leak into before/after"""
        set_module_args({
            'config': {'timezone': 'Etc/UTC'},
            'gather_time': True,
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertNotIn('time', result['before'])
        self.assertNotIn('time', result.get('after', {}))
