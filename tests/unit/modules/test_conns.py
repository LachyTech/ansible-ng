# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import conns
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestConnsModule(TestModuleBase):

    module = conns

    def setUp(self):
        super(TestConnsModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.conns.ConnsFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestConnsModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("conns_config.cfg")
        self.get_device_data.side_effect = load_from_file

    # ── Idempotency ──────────────────────────────────────────────────────────

    def test_conns_merged_idempotent(self):
        """No change when desired state already matches device."""
        set_module_args({
            'config': [
                {
                    'name': 'default-conn-1',
                    'mode': 'static',
                    'physif': 'system_net_physifs-1',
                    'description': 'Primary static IPv4',
                }
            ],
            'state': 'merged',
        })
        self.execute_module(changed=False, commands=[])

    def test_conns_replaced_idempotent(self):
        """No change when replaced config already matches device."""
        set_module_args({
            'config': [
                {
                    'name': 'default-conn-2',
                    'mode': 'dhcp',
                    'physif': 'system_net_physifs-1',
                }
            ],
            'state': 'replaced',
        })
        self.execute_module(changed=False, commands=[])

    # ── Merged state ─────────────────────────────────────────────────────────

    def test_conns_merged_adds_description(self):
        """Merged update adds description to an existing conn."""
        set_module_args({
            'config': [
                {
                    'name': 'default-conn-2',
                    'description': 'DHCP on net1',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        cmd = result['commands'][0]
        self.assertEqual(cmd['method'], 'PUT')
        self.assertEqual(cmd['path'], 'conns/system_net_conns-2')
        self.assertEqual(cmd['data']['conn']['description'], 'DHCP on net1')

    def test_conns_merged_by_id(self):
        """Identify conn by id when name is not provided."""
        set_module_args({
            'config': [
                {
                    'id': 'system_net_conns-4',
                    'description': 'Secondary DHCP',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.assertEqual(result['commands'][0]['method'], 'PUT')
        self.assertEqual(result['commands'][0]['path'], 'conns/system_net_conns-4')

    def test_conns_merged_post_new_conn(self):
        """A conn with no matching name triggers a POST."""
        set_module_args({
            'config': [
                {
                    'mode': 'static',
                    'physif': 'system_net_physifs-2',
                    'ipv4_static_settings': {
                        'address': '10.0.0.1',
                        'netmask': '255.255.255.0',
                        'gateway': '10.0.0.254',
                    },
                }
            ],
            'state': 'merged',
        })
        commands = [
            {
                'path': 'conns/',
                'data': {
                    'conn': {
                        'mode': 'static',
                        'physif': 'system_net_physifs-2',
                        'ipv4_static_settings': {
                            'address': '10.0.0.1',
                            'netmask': '255.255.255.0',
                            'gateway': '10.0.0.254',
                        },
                    }
                },
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_conns_merged_strips_id_and_name_from_body(self):
        """id and name are never included in PUT/POST bodies."""
        set_module_args({
            'config': [
                {
                    'name': 'default-conn-1',
                    'description': 'Updated description',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['conn']
        self.assertNotIn('id', body)
        self.assertNotIn('name', body)

    def test_conns_merged_preserves_device_fields(self):
        """Merged sends the full merged body, preserving unspecified device fields."""
        set_module_args({
            'config': [
                {
                    'name': 'default-conn-1',
                    'description': 'Updated',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['conn']
        # mode and physif were on the device and should be preserved in the merged body
        self.assertEqual(body['mode'], 'static')
        self.assertEqual(body['physif'], 'system_net_physifs-1')

    # ── Replaced state ───────────────────────────────────────────────────────

    def test_conns_replaced_update(self):
        """Replaced sends only the specified fields (not merged with device state)."""
        set_module_args({
            'config': [
                {
                    'name': 'default-conn-1',
                    'mode': 'dhcp',
                    'physif': 'system_net_physifs-1',
                }
            ],
            'state': 'replaced',
        })
        commands = [
            {
                'path': 'conns/system_net_conns-1',
                'data': {
                    'conn': {
                        'mode': 'dhcp',
                        'physif': 'system_net_physifs-1',
                    }
                },
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # ── Overridden state ─────────────────────────────────────────────────────

    def test_conns_overridden_deletes_absent_conns(self):
        """Overridden deletes conns not present in want."""
        set_module_args({
            'config': [
                {'name': 'default-conn-1', 'mode': 'static', 'physif': 'system_net_physifs-1',
                 'description': 'Primary static IPv4'},
                {'name': 'default-conn-2', 'mode': 'dhcp', 'physif': 'system_net_physifs-1'},
            ],
            'state': 'overridden',
        })
        result = self.execute_module(changed=True)
        delete_paths = [c['path'] for c in result['commands'] if c['method'] == 'DELETE']
        # conns 3, 4, 5 should be deleted
        self.assertIn('conns/system_net_conns-3', delete_paths)
        self.assertIn('conns/system_net_conns-4', delete_paths)
        self.assertIn('conns/system_net_conns-5', delete_paths)
        # conns 1 and 2 should not be deleted
        self.assertNotIn('conns/system_net_conns-1', delete_paths)
        self.assertNotIn('conns/system_net_conns-2', delete_paths)

    # ── Deleted state ────────────────────────────────────────────────────────

    def test_conns_deleted_by_name(self):
        """Delete a conn by name."""
        set_module_args({
            'config': [{'name': 'default-conn-2'}],
            'state': 'deleted',
        })
        commands = [
            {
                'path': 'conns/system_net_conns-2',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_conns_deleted_nonexistent_skipped(self):
        """Deleting a conn that does not exist produces no commands."""
        set_module_args({
            'config': [{'name': 'does-not-exist'}],
            'state': 'deleted',
        })
        self.execute_module(changed=False, commands=[])

    # ── Gathered / Rendered ──────────────────────────────────────────────────

    def test_conns_gathered(self):
        """Gathered state returns all conns from device."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        self.assertEqual(len(result['gathered']), 5)
        names = [c['name'] for c in result['gathered']]
        self.assertIn('default-conn-1', names)
        self.assertIn('v6-dyn-n1-conn', names)

    def test_conns_gathered_strips_runtime_status(self):
        """runtime_status is excluded from gathered facts."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        for conn in result['gathered']:
            self.assertNotIn('runtime_status', conn)

    def test_conns_gathered_includes_description(self):
        """description field is present in gathered facts when set on device."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        conn1 = next(c for c in result['gathered'] if c['name'] == 'default-conn-1')
        self.assertEqual(conn1['description'], 'Primary static IPv4')

    def test_conns_gathered_includes_static_settings(self):
        """ipv4_static_settings are present in gathered facts."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        conn1 = next(c for c in result['gathered'] if c['name'] == 'default-conn-1')
        self.assertIn('ipv4_static_settings', conn1)
        self.assertEqual(conn1['ipv4_static_settings']['address'], '192.168.1.100')

    def test_conns_rendered(self):
        """Rendered state generates commands without contacting the device."""
        set_module_args({
            'config': [
                {
                    'mode': 'dhcp',
                    'physif': 'system_net_physifs-2',
                }
            ],
            'state': 'rendered',
        })
        result = self.execute_module(changed=False)
        self.assertIn('rendered', result)
        self.get_device_data.assert_not_called()

    # ── Check mode ───────────────────────────────────────────────────────────

    def test_conns_check_mode(self):
        """Check mode generates commands but does not call send_request."""
        set_module_args({
            '_ansible_check_mode': True,
            'config': [
                {
                    'name': 'default-conn-2',
                    'description': 'Check mode update',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()

    # ── Diff mode ────────────────────────────────────────────────────────────

    def test_conns_diff_merged_update(self):
        """Diff output shows before and after for a merged update."""
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'name': 'default-conn-1',
                    'description': 'Updated via Ansible',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(len(after), 1)
        self.assertEqual(before[0]['name'], 'default-conn-1')
        self.assertEqual(after[0]['description'], 'Updated via Ansible')

    def test_conns_diff_deleted(self):
        """Diff output for deleted shows before as old config, after as empty dict."""
        set_module_args({
            '_ansible_diff': True,
            'config': [{'name': 'default-conn-2'}],
            'state': 'deleted',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(before[0]['name'], 'default-conn-2')
        self.assertEqual(after[0], {})

    def test_conns_no_diff_when_not_requested(self):
        """Diff key is absent when _ansible_diff is not set."""
        set_module_args({
            'config': [{'name': 'default-conn-2', 'description': 'Updated'}],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_conns_no_diff_when_idempotent(self):
        """Diff key is absent when there are no changes."""
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'name': 'default-conn-2',
                    'mode': 'dhcp',
                    'physif': 'system_net_physifs-1',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_conns_check_mode_with_diff(self):
        """Check mode with diff generates diff without sending commands."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {
                    'name': 'default-conn-1',
                    'description': 'Check mode diff',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before[0]['description'], 'Primary static IPv4')
        self.assertEqual(after[0]['description'], 'Check mode diff')

    # ── Deprecation warnings ─────────────────────────────────────────────────

    def test_conns_dns1_deprecation_warning(self):
        """Using ipv4_static_settings.dns1 emits a deprecation warning."""
        set_module_args({
            'config': [
                {
                    'mode': 'static',
                    'physif': 'system_net_physifs-2',
                    'ipv4_static_settings': {
                        'address': '10.0.0.1',
                        'netmask': '255.255.255.0',
                        'dns1': '8.8.8.8',
                    },
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        warnings = result.get('warnings', [])
        self.assertTrue(
            any('dns1' in w and 'deprecated' in w for w in warnings),
            msg="Expected dns1 deprecation warning, got: {0}".format(warnings),
        )

    def test_conns_dns2_deprecation_warning_ipv6(self):
        """Using ipv6_static_settings.dns2 emits a deprecation warning."""
        set_module_args({
            'config': [
                {
                    'mode': 'ipv6_static',
                    'physif': 'system_net_physifs-2',
                    'ipv6_static_settings': {
                        'address': '2001:db8::1',
                        'prefix_length': 64,
                        'dns2': '2001:4860:4860::8888',
                    },
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        warnings = result.get('warnings', [])
        self.assertTrue(
            any('dns2' in w and 'deprecated' in w for w in warnings),
            msg="Expected dns2 deprecation warning, got: {0}".format(warnings),
        )

    def test_conns_dns_warning_deduped(self):
        """Deprecation warning is emitted only once even when multiple conns use dns1."""
        set_module_args({
            'config': [
                {
                    'mode': 'static',
                    'physif': 'system_net_physifs-1',
                    'ipv4_static_settings': {'address': '10.0.0.1', 'netmask': '255.0.0.0', 'dns1': '8.8.8.8'},
                },
                {
                    'mode': 'static',
                    'physif': 'system_net_physifs-2',
                    'ipv4_static_settings': {'address': '10.0.0.2', 'netmask': '255.0.0.0', 'dns1': '8.8.8.8'},
                },
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        dns1_warnings = [w for w in result.get('warnings', []) if 'dns1' in w and 'deprecated' in w]
        self.assertEqual(len(dns1_warnings), 1)

    # ── prefix_length type ───────────────────────────────────────────────────

    def test_conns_prefix_length_as_int(self):
        """prefix_length is accepted and returned as an integer."""
        set_module_args({
            'config': [
                {
                    'mode': 'ipv6_static',
                    'physif': 'system_net_physifs-2',
                    'ipv6_static_settings': {
                        'address': '2001:db8::1',
                        'prefix_length': 64,
                        'gateway': '2001:db8::fe',
                    },
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['conn']
        self.assertIsInstance(body['ipv6_static_settings']['prefix_length'], int)
        self.assertEqual(body['ipv6_static_settings']['prefix_length'], 64)
