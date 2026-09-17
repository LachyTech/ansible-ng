# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import local_password_policy
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestLocalPasswordPolicyModule(TestModuleBase):

    module = local_password_policy

    def setUp(self):
        super(TestLocalPasswordPolicyModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.local_password_policy.LocalPasswordPolicyFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestLocalPasswordPolicyModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("local_password_policy_config.cfg")
        self.get_device_data.side_effect = load_from_file

    # ── Idempotency ──────────────────────────────────────────────────────────

    def test_local_password_policy_merged_idempotent(self):
        """No change when desired state already matches device."""
        set_module_args({
            'config': {
                'password_complexity_enabled': True,
                'password_minimum_length': 10,
            },
            'state': 'merged',
        })
        self.execute_module(changed=False, commands=[])

    def test_local_password_policy_replaced_idempotent(self):
        """No change when replaced config is a subset of device state."""
        set_module_args({
            'config': {
                'password_expiry_interval_enabled': False,
                'password_complexity_enabled': True,
                'password_minimum_length': 10,
                'password_must_contain_upper_case': True,
                'password_must_contain_special': False,
                'password_must_contain_number': True,
                'password_disallow_username': True,
            },
            'state': 'replaced',
        })
        self.execute_module(changed=False, commands=[])

    # ── Merged state ─────────────────────────────────────────────────────────

    def test_local_password_policy_merged_enable_expiry(self):
        """Merged update enables expiry and preserves unspecified fields."""
        set_module_args({
            'config': {
                'password_expiry_interval_enabled': True,
                'password_expiry_interval_days': 30,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        cmd = result['commands'][0]
        self.assertEqual(cmd['method'], 'PUT')
        self.assertEqual(cmd['path'], 'local_password_policy')
        body = cmd['data']['local_password_policy']
        self.assertTrue(body['password_expiry_interval_enabled'])
        self.assertEqual(body['password_expiry_interval_days'], 30)
        # Unspecified fields should be preserved from device state
        self.assertTrue(body['password_complexity_enabled'])
        self.assertEqual(body['password_minimum_length'], 10)

    def test_local_password_policy_merged_raise_minimum_length(self):
        """Merged update raises the minimum length requirement."""
        set_module_args({
            'config': {
                'password_minimum_length': 14,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['local_password_policy']
        self.assertEqual(body['password_minimum_length'], 14)
        self.assertTrue(body['password_complexity_enabled'])

    def test_local_password_policy_merged_disallow_username(self):
        """Merged update toggles password_disallow_username."""
        set_module_args({
            'config': {
                'password_disallow_username': False,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['local_password_policy']
        self.assertFalse(body['password_disallow_username'])

    def test_local_password_policy_merged_preserves_device_fields(self):
        """Merged sends a fully merged body so unspecified device fields are not lost."""
        set_module_args({
            'config': {
                'password_complexity_enabled': False,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['local_password_policy']
        self.assertIn('password_minimum_length', body)
        self.assertIn('password_must_contain_upper_case', body)
        self.assertIn('password_must_contain_number', body)
        self.assertIn('password_disallow_username', body)

    # ── Replaced / Overridden state ───────────────────────────────────────────

    def test_local_password_policy_replaced_merges_like_merged(self):
        """Replaced merges with device state, since the API requires every
        field on each request and there is no way to omit or clear one."""
        set_module_args({
            'config': {
                'password_complexity_enabled': True,
                'password_minimum_length': 8,
            },
            'state': 'replaced',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['local_password_policy']
        self.assertEqual(body['password_complexity_enabled'], True)
        self.assertEqual(body['password_minimum_length'], 8)
        # Device-only fields are preserved from device state, not dropped
        self.assertIn('password_must_contain_upper_case', body)
        self.assertIn('password_disallow_username', body)

    def test_local_password_policy_overridden_same_as_replaced(self):
        """Overridden behaves identically to replaced for a singleton resource."""
        set_module_args({
            'config': {
                'password_complexity_enabled': True,
                'password_minimum_length': 12,
            },
            'state': 'overridden',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.assertEqual(result['commands'][0]['method'], 'PUT')

    # ── Gathered / Rendered ──────────────────────────────────────────────────

    def test_local_password_policy_gathered(self):
        """Gathered state returns the current policy from the device."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        gathered = result['gathered']
        self.assertEqual(gathered['password_expiry_interval_enabled'], False)
        self.assertEqual(gathered['password_expiry_interval_days'], 90)
        self.assertEqual(gathered['password_complexity_enabled'], True)
        self.assertEqual(gathered['password_minimum_length'], 10)
        self.assertEqual(gathered['password_must_contain_upper_case'], True)
        self.assertEqual(gathered['password_must_contain_special'], False)
        self.assertEqual(gathered['password_must_contain_number'], True)
        self.assertEqual(gathered['password_disallow_username'], True)

    def test_local_password_policy_rendered(self):
        """Rendered state generates commands without contacting the device."""
        set_module_args({
            'config': {
                'password_complexity_enabled': True,
                'password_minimum_length': 10,
            },
            'state': 'rendered',
        })
        result = self.execute_module(changed=False)
        self.assertIn('rendered', result)
        self.get_device_data.assert_not_called()

    # ── Check mode ───────────────────────────────────────────────────────────

    def test_local_password_policy_check_mode(self):
        """Check mode generates commands but does not call send_request."""
        set_module_args({
            '_ansible_check_mode': True,
            'config': {
                'password_minimum_length': 12,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()

    # ── Diff mode ────────────────────────────────────────────────────────────

    def test_local_password_policy_diff_merged_update(self):
        """Diff output shows before and after for a merged update."""
        set_module_args({
            '_ansible_diff': True,
            'config': {
                'password_minimum_length': 14,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before['password_minimum_length'], 10)
        self.assertEqual(after['password_minimum_length'], 14)

    def test_local_password_policy_no_diff_when_not_requested(self):
        """Diff key is absent when _ansible_diff is not set."""
        set_module_args({
            'config': {'password_minimum_length': 14},
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_local_password_policy_no_diff_when_idempotent(self):
        """Diff key is absent when there are no changes."""
        set_module_args({
            '_ansible_diff': True,
            'config': {
                'password_complexity_enabled': True,
                'password_minimum_length': 10,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_local_password_policy_check_mode_with_diff(self):
        """Check mode with diff generates diff without sending commands."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': {
                'password_minimum_length': 16,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before['password_minimum_length'], 10)
        self.assertEqual(after['password_minimum_length'], 16)

    # ── commands key always present ───────────────────────────────────────────

    def test_local_password_policy_commands_always_present(self):
        """result['commands'] is always present, even when there are no changes."""
        set_module_args({
            'config': {
                'password_complexity_enabled': True,
                'password_minimum_length': 10,
            },
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertIn('commands', result)
        self.assertEqual(result['commands'], [])
