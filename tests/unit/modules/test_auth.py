# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import auth
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestAuthModule(TestModuleBase):

    module = auth

    def setUp(self):
        super(TestAuthModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.auth.AuthFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestAuthModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.side_effect = lambda *a, **kw: load_fixture("auth_config.cfg")

    # --- merged state ---

    def test_auth_merged_noop(self):
        set_module_args({
            'config': {
                'mode': 'local',
                'policy': 'remotelocal',
                'timeout': 10,
            },
            'state': 'merged',
        })
        self.execute_module(changed=False, commands=[])

    def test_auth_merged_change_timeout(self):
        set_module_args({
            'config': {
                'timeout': 30,
            },
            'state': 'merged',
        })
        commands = [
            {
                'path': 'auth',
                'data': {
                    'auth': {
                        'mode': 'local',
                        'policy': 'remotelocal',
                        'timeout': 30,
                    }
                },
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_auth_merged_change_mode(self):
        set_module_args({
            'config': {
                'mode': 'ldap',
                'policy': 'remotedownlocal',
                'ldapBaseDN': 'dc=example,dc=com',
                'ldapUsernameAttribute': 'uid',
                'ldapAuthenticationServers': [
                    {'hostname': 'ldap.example.com', 'port': 389}
                ],
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        cmd = result['commands'][0]
        self.assertEqual(cmd['method'], 'PUT')
        self.assertEqual(cmd['path'], 'auth')
        auth_data = cmd['data']['auth']
        self.assertEqual(auth_data['mode'], 'ldap')
        self.assertEqual(auth_data['ldapBaseDN'], 'dc=example,dc=com')
        self.assertIn('ldapAuthenticationServers', auth_data)

    def test_auth_merged_with_ldap_servers_always_updates(self):
        """Server list fields always trigger a PUT in merged mode."""
        set_module_args({
            'config': {
                'ldapAuthenticationServers': [
                    {'hostname': 'ldap.example.com', 'port': 389}
                ],
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)

    # --- replaced / overridden state ---

    def test_auth_replaced(self):
        """replaced with different timeout and missing policy removes policy."""
        set_module_args({
            'config': {
                'mode': 'local',
                'timeout': 20,
            },
            'state': 'replaced',
        })
        commands = [
            {
                'path': 'auth',
                'data': {
                    'auth': {
                        'mode': 'local',
                        'timeout': 20,
                    }
                },
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_auth_replaced_noop(self):
        set_module_args({
            'config': {
                'mode': 'local',
                'policy': 'remotelocal',
                'timeout': 10,
            },
            'state': 'replaced',
        })
        self.execute_module(changed=False, commands=[])

    def test_auth_overridden(self):
        """overridden behaves the same as replaced."""
        set_module_args({
            'config': {
                'mode': 'local',
                'timeout': 20,
            },
            'state': 'overridden',
        })
        commands = [
            {
                'path': 'auth',
                'data': {
                    'auth': {
                        'mode': 'local',
                        'timeout': 20,
                    }
                },
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- gathered / rendered ---

    def test_auth_gathered(self):
        set_module_args({
            'state': 'gathered',
        })
        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        gathered = result['gathered']
        self.assertEqual(gathered['mode'], 'local')
        self.assertEqual(gathered['policy'], 'remotelocal')
        self.assertEqual(gathered['timeout'], 10)

    def test_auth_rendered(self):
        set_module_args({
            'config': {
                'mode': 'ldap',
                'ldapBaseDN': 'dc=example,dc=com',
            },
            'state': 'rendered',
        })
        self.execute_module(changed=False, commands=[])

    # --- check mode ---

    def test_auth_check_mode(self):
        set_module_args({
            '_ansible_check_mode': True,
            'config': {
                'timeout': 30,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()

    # --- diff mode ---

    def test_auth_diff_merged(self):
        set_module_args({
            '_ansible_diff': True,
            'config': {
                'timeout': 30,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before['timeout'], 10)
        self.assertEqual(after['timeout'], 30)
        self.assertEqual(before['mode'], 'local')
        self.assertEqual(after['mode'], 'local')

    def test_auth_no_diff_when_not_requested(self):
        set_module_args({
            'config': {
                'timeout': 30,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_auth_no_diff_when_idempotent(self):
        set_module_args({
            '_ansible_diff': True,
            'config': {
                'mode': 'local',
                'policy': 'remotelocal',
                'timeout': 10,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    # --- check mode + diff ---

    def test_auth_check_mode_with_diff(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': {
                'timeout': 30,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before['timeout'], 10)
        self.assertEqual(after['timeout'], 30)
        self.assertNotEqual(before['timeout'], after['timeout'])

    def test_auth_check_mode_with_diff_replaced(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': {
                'mode': 'local',
                'timeout': 20,
            },
            'state': 'replaced',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before['timeout'], 10)
        self.assertEqual(after['timeout'], 20)
        # policy was in before but not in after (replaced removes it)
        self.assertIn('policy', before)
        self.assertNotIn('policy', after)

    def test_auth_sensitive_field_not_in_diff(self):
        """Sensitive fields must not appear in diff output."""
        set_module_args({
            '_ansible_diff': True,
            'config': {
                'mode': 'radius',
                'radiusPassword': 's3cr3t',
                'radiusAuthenticationServers': [
                    {'hostname': 'radius.example.com', 'port': 1812}
                ],
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        after = json.loads(result['diff']['after'])
        self.assertNotIn('radiusPassword', after)
