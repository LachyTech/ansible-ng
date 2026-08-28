# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import system_config
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestSystemConfigModule(TestModuleBase):

    module = system_config

    def setUp(self):
        super(TestSystemConfigModule, self).setUp()
        self.maxDiff = None

        # Mock the per-field device fetch used to build the current settings.
        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.system_config.SystemConfigFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestSystemConfigModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("system_config.cfg")

    # --- merged ---
    def test_system_merged_change_scalar(self):
        """Changing a scalar setting emits a single PUT for that endpoint"""
        set_module_args({
            'config': {'banner': 'New banner text'},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/banner',
                'data': {'system_banner': {'banner': 'New banner text'}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_system_merged_idempotent(self):
        """Merging a value already present produces no commands"""
        set_module_args({
            'config': {'banner': 'Authorized access only', 'ssh_port': 22},
            'state': 'merged',
        })

        self.execute_module(changed=False, commands=[])

    def test_system_merged_multiple_endpoints(self):
        """Multiple changed settings map to one PUT per endpoint"""
        set_module_args({
            'config': {'ssh_port': 2222, 'fips': {'enabled': True}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/ssh_port',
                'data': {'system_ssh_port': {'port': 2222}},
                'method': 'PUT',
            },
            {
                'path': 'system/fips',
                'data': {'fips': {'enabled': True}},
                'method': 'PUT',
            },
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(
            sorted(result['commands'], key=lambda c: c['path']),
            sorted(commands, key=lambda c: c['path']),
        )

    def test_system_merged_fips(self):
        """Enabling FIPS emits a PUT to the fips endpoint"""
        set_module_args({
            'config': {'fips': {'enabled': True}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/fips',
                'data': {'fips': {'enabled': True}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_system_merged_session_timeout_partial(self):
        """A partial session_timeout dict pushes only the changed sub-field"""
        set_module_args({
            'config': {'session_timeout': {'webui_timeout': 60}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/session_timeout',
                'data': {'system_session_timeout': {'webui_timeout': 60}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_system_merged_admin_info_partial(self):
        """A partial admin_info dict pushes only the changed sub-field"""
        set_module_args({
            'config': {'admin_info': {'location': 'Server Room B, Rack 9'}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/admin_info',
                'data': {'system_admin_info': {'location': 'Server Room B, Rack 9'}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- replaced ---
    def test_system_replaced_behaves_like_merged(self):
        """replaced on a singleton only touches provided fields"""
        set_module_args({
            'config': {'banner': 'New banner'},
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'system/banner',
                'data': {'system_banner': {'banner': 'New banner'}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- gathered ---
    def test_system_gathered(self):
        """gathered returns the current settings as unwrapped config"""
        set_module_args({'state': 'gathered'})

        result = self.execute_module(changed=False)

        gathered = result['gathered']
        self.assertEqual(gathered['banner'], 'Authorized access only')
        self.assertEqual(gathered['ssh_port'], 22)
        self.assertEqual(gathered['admin_info']['contact'], 'netops@example.com')
        self.assertEqual(gathered['session_timeout']['cli_timeout'], 30)
        self.assertEqual(gathered['session_timeout']['webui_timeout'], 30)
        self.assertEqual(gathered['fips']['enabled'], False)
        # time/timezone are managed by the system_time module, not here
        self.assertNotIn('timezone', gathered)
        self.assertNotIn('time', gathered)

    # --- rendered ---
    def test_system_rendered(self):
        """rendered returns the commands without contacting the device"""
        set_module_args({
            'config': {'banner': 'Rendered banner'},
            'state': 'rendered',
        })

        result = self.execute_module(changed=False)
        self.assertEqual(
            result['rendered'],
            [
                {
                    'path': 'system/banner',
                    'data': {'system_banner': {'banner': 'Rendered banner'}},
                    'method': 'PUT',
                }
            ],
        )

    # --- diff mode ---

    def test_diff_mode_when_changed(self):
        """diff key is present when _ansible_diff is set and a change is made"""
        set_module_args({
            '_ansible_diff': True,
            'config': {'banner': 'New banner'},
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertIn('banner', before)
        self.assertIn('banner', after)

    def test_no_diff_when_not_requested(self):
        """diff key is absent when _ansible_diff is not set"""
        set_module_args({
            'config': {'banner': 'New banner'},
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_no_diff_when_idempotent(self):
        """diff key is absent when nothing changed"""
        set_module_args({
            '_ansible_diff': True,
            'config': {'banner': 'Authorized access only'},
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)
