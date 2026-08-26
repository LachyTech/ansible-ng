# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import physifs
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestPhysifsModule(TestModuleBase):

    module = physifs

    def setUp(self):
        super(TestPhysifsModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.physifs.PhysifsFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestPhysifsModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("physifs_config.cfg")
        self.get_device_data.side_effect = load_from_file

    # ── Idempotency ──────────────────────────────────────────────────────────

    def test_physifs_merged_idempotent(self):
        """No change when desired state already matches device."""
        set_module_args({
            'config': [
                {
                    'name': 'init_net1',
                    'enabled': True,
                    'description': '1G Copper',
                    'mtu': 1500,
                    'ethernet_setting': {'link_speed': 'auto'},
                }
            ],
            'state': 'merged',
        })
        self.execute_module(changed=False, commands=[])

    def test_physifs_replaced_idempotent(self):
        """No change when replaced config already matches device."""
        set_module_args({
            'config': [
                {
                    'name': 'init_net1',
                    'enabled': True,
                    'description': '1G Copper',
                    'mtu': 1500,
                    'ethernet_setting': {'link_speed': 'auto'},
                }
            ],
            'state': 'replaced',
        })
        self.execute_module(changed=False, commands=[])

    # ── Merged state ─────────────────────────────────────────────────────────

    def test_physifs_update_merged(self):
        """Merged update preserves unspecified device fields."""
        set_module_args({
            'config': [
                {
                    'name': 'init_net1',
                    'description': 'Primary management',
                    'mtu': 1400,
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'physifs/system_net_physifs-1',
                'data': {
                    'physif': {
                        'enabled': True,
                        'description': 'Primary management',
                        'media': 'ethernet',
                        'mtu': 1400,
                        'device': 'net1',
                        'slaves': [],
                        'dns': {'nameservers': [], 'search_domains': []},
                        'ethernet_setting': {'link_speed': 'auto'},
                    }
                },
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_physifs_merge_by_id(self):
        """Identify interface by id when name is not provided."""
        set_module_args({
            'config': [
                {
                    'id': 'system_net_physifs-2',
                    'description': 'Secondary link',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.assertEqual(result['commands'][0]['method'], 'PUT')
        self.assertEqual(result['commands'][0]['path'], 'physifs/system_net_physifs-2')

    def test_physifs_merged_dns(self):
        """Merged update can configure DNS settings."""
        set_module_args({
            'config': [
                {
                    'name': 'init_net1',
                    'dns': {
                        'nameservers': ['8.8.8.8', '8.8.4.4'],
                        'search_domains': ['example.com'],
                    },
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['physif']
        self.assertEqual(body['dns']['nameservers'], ['8.8.8.8', '8.8.4.4'])
        self.assertEqual(body['dns']['search_domains'], ['example.com'])

    def test_physifs_create_aggregate_merged(self):
        """A new aggregate interface with no matching name triggers a POST."""
        set_module_args({
            'config': [
                {
                    'enabled': True,
                    'media': 'bond',
                    'device': 'bnd1',
                    'slaves': ['net1', 'net2'],
                    'bond_setting': {'mode': 'active-backup'},
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'physifs/',
                'data': {
                    'physif': {
                        'enabled': True,
                        'media': 'bond',
                        'device': 'bnd1',
                        'slaves': ['net1', 'net2'],
                        'bond_setting': {'mode': 'active-backup'},
                    }
                },
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # ── Replaced state ───────────────────────────────────────────────────────

    def test_physifs_update_replaced(self):
        """Replaced sets exactly what is specified, not a superset."""
        set_module_args({
            'config': [
                {
                    'name': 'init_net1',
                    'enabled': True,
                    'description': 'Replaced description',
                    'mtu': 1400,
                    'ethernet_setting': {'link_speed': '100mbps-fd'},
                }
            ],
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'physifs/system_net_physifs-1',
                'data': {
                    'physif': {
                        'enabled': True,
                        'description': 'Replaced description',
                        'mtu': 1400,
                        'ethernet_setting': {'link_speed': '100mbps-fd'},
                    }
                },
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # ── Overridden state ─────────────────────────────────────────────────────

    def test_physifs_overridden_deletes_aggregate(self):
        """Overridden deletes aggregate physifs not present in want."""
        set_module_args({
            'config': [
                {
                    'name': 'init_net1',
                    'enabled': True,
                    'description': '1G Copper',
                    'mtu': 1500,
                    'ethernet_setting': {'link_speed': 'auto'},
                },
                {
                    'name': 'init_net2',
                    'enabled': True,
                    'description': '1G Copper',
                    'mtu': 1500,
                    'ethernet_setting': {'link_speed': 'auto'},
                },
                {
                    'name': 'init_cellular',
                    'enabled': False,
                },
            ],
            'state': 'overridden',
        })
        result = self.execute_module(changed=True)
        methods = [c['method'] for c in result['commands']]
        # Bond (init_bond0) should be deleted; ethernet/cellular cannot be deleted
        self.assertIn('DELETE', methods)
        delete_cmds = [c for c in result['commands'] if c['method'] == 'DELETE']
        self.assertEqual(len(delete_cmds), 1)
        self.assertIn('system_net_physifs-4', delete_cmds[0]['path'])

    def test_physifs_overridden_skips_non_aggregate_delete(self):
        """Overridden never deletes ethernet or cellular interfaces."""
        set_module_args({
            'config': [
                {
                    'name': 'init_bond0',
                    'enabled': True,
                    'media': 'bond',
                    'slaves': ['net1', 'net2'],
                    'bond_setting': {'mode': 'active-backup'},
                },
            ],
            'state': 'overridden',
        })
        result = self.execute_module(changed=True)
        delete_paths = [c['path'] for c in result['commands'] if c['method'] == 'DELETE']
        # net1, net2, cellular should never be deleted
        self.assertNotIn('system_net_physifs-1', str(delete_paths))
        self.assertNotIn('system_net_physifs-2', str(delete_paths))
        self.assertNotIn('system_net_physifs-3', str(delete_paths))

    # ── Deleted state ────────────────────────────────────────────────────────

    def test_physifs_deleted_aggregate(self):
        """Delete an aggregate interface by name."""
        set_module_args({
            'config': [{'name': 'init_bond0'}],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'physifs/system_net_physifs-4',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_physifs_deleted_ethernet_skipped(self):
        """Attempting to delete a non-aggregate interface produces no commands."""
        set_module_args({
            'config': [{'name': 'init_net1'}],
            'state': 'deleted',
        })
        self.execute_module(changed=False, commands=[])

    def test_physifs_deleted_nonexistent_skipped(self):
        """Deleting an interface that does not exist produces no commands."""
        set_module_args({
            'config': [{'name': 'init_does_not_exist'}],
            'state': 'deleted',
        })
        self.execute_module(changed=False, commands=[])

    # ── Gathered / Rendered ──────────────────────────────────────────────────

    def test_physifs_gathered(self):
        """Gathered state returns all interfaces from device."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        ifaces = result['gathered']
        self.assertEqual(len(ifaces), 4)
        names = [i['name'] for i in ifaces]
        self.assertIn('init_net1', names)
        self.assertIn('init_cellular', names)
        self.assertIn('init_bond0', names)

    def test_physifs_gathered_facts_are_media_specific(self):
        """Gathered facts only contain settings relevant to each media type."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        net1 = next(i for i in result['gathered'] if i['name'] == 'init_net1')
        # Ethernet interface must not have cellular or bridge settings
        self.assertNotIn('cellular_setting', net1)
        self.assertNotIn('bridge_setting', net1)
        self.assertNotIn('bond_setting', net1)
        self.assertIn('ethernet_setting', net1)

    def test_physifs_gathered_strips_readonly_subfields(self):
        """read-only API sub-fields are stripped from gathered facts."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)

        net1 = next(i for i in result['gathered'] if i['name'] == 'init_net1')
        self.assertNotIn('available_link_speeds', net1.get('ethernet_setting', {}))

        cellular = next(i for i in result['gathered'] if i['name'] == 'init_cellular')
        self.assertNotIn('available_carrier_firmwares', cellular.get('cellular_setting', {}))
        for sim in cellular.get('cellular_setting', {}).get('sims', []):
            self.assertNotIn('id', sim)
            self.assertNotIn('runtime_status', sim)

    def test_physifs_gathered_strips_readonly_top_level(self):
        """Top-level read-only API fields are excluded from gathered facts."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        net1 = next(i for i in result['gathered'] if i['name'] == 'init_net1')
        self.assertNotIn('runtime_status', net1)
        self.assertNotIn('mac_address', net1)
        self.assertNotIn('master', net1)

    def test_physifs_rendered(self):
        """Rendered state generates commands without contacting the device."""
        set_module_args({
            'config': [
                {
                    'enabled': True,
                    'media': 'bond',
                    'device': 'bnd1',
                    'slaves': ['net1', 'net2'],
                    'bond_setting': {'mode': 'active-backup'},
                }
            ],
            'state': 'rendered',
        })
        result = self.execute_module(changed=False)
        self.assertIn('rendered', result)

    # ── Check mode ───────────────────────────────────────────────────────────

    def test_physifs_check_mode(self):
        """Check mode generates commands but does not send them."""
        set_module_args({
            '_ansible_check_mode': True,
            'config': [
                {
                    'name': 'init_net1',
                    'description': 'Check mode update',
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()

    # ── Diff mode ────────────────────────────────────────────────────────────

    def test_physifs_diff_merged_update(self):
        """Diff output shows before and after for a merged update."""
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'name': 'init_net1',
                    'description': 'Updated via Ansible',
                    'mtu': 1400,
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
        self.assertEqual(before[0]['name'], 'init_net1')
        self.assertEqual(after[0]['mtu'], 1400)
        self.assertEqual(after[0]['description'], 'Updated via Ansible')

    def test_physifs_diff_deleted(self):
        """Diff output for deleted shows before as the old config and after as empty."""
        set_module_args({
            '_ansible_diff': True,
            'config': [{'name': 'init_bond0'}],
            'state': 'deleted',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(before[0]['name'], 'init_bond0')
        self.assertEqual(after[0], {})

    def test_physifs_no_diff_when_not_requested(self):
        """Diff key is absent when _ansible_diff is not set."""
        set_module_args({
            'config': [{'name': 'init_net1', 'description': 'Updated'}],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_physifs_no_diff_when_idempotent(self):
        """Diff key is absent when there are no changes."""
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'name': 'init_net1',
                    'enabled': True,
                    'description': '1G Copper',
                    'mtu': 1500,
                    'ethernet_setting': {'link_speed': 'auto'},
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_physifs_check_mode_with_diff(self):
        """Check mode with diff generates diff without sending commands."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {
                    'name': 'init_net1',
                    'description': 'Check mode diff',
                    'mtu': 1400,
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before[0]['description'], '1G Copper')
        self.assertEqual(after[0]['mtu'], 1400)

    # ── Cellular settings ────────────────────────────────────────────────────

    def test_physifs_cellular_merged_idempotent(self):
        """No change when cellular config already matches device."""
        set_module_args({
            'config': [
                {
                    'name': 'init_cellular',
                    'enabled': False,
                    'cellular_setting': {
                        'active_sim': 1,
                        'sim_failover_policy': 'never',
                        'sim_failback_policy': 'never',
                        'sims': [
                            {'slot': 1, 'apn': 'internet', 'iptype': 'IPv4v6'},
                            {'slot': 2, 'apn': 'backup.internet', 'iptype': 'IPv4v6'},
                        ],
                    },
                }
            ],
            'state': 'merged',
        })
        self.execute_module(changed=False, commands=[])

    def test_physifs_cellular_merged_update_sim_apn(self):
        """Merged update on one SIM field updates only that slot."""
        set_module_args({
            'config': [
                {
                    'name': 'init_cellular',
                    'cellular_setting': {
                        'sims': [
                            {'slot': 1, 'apn': 'new.apn'},
                        ],
                    },
                }
            ],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        body = result['commands'][0]['data']['physif']
        sims = body['cellular_setting']['sims']
        # Slot 1 should have updated APN; slot 2 should be preserved
        slot1 = next(s for s in sims if s['slot'] == 1)
        slot2 = next(s for s in sims if s['slot'] == 2)
        self.assertEqual(slot1['apn'], 'new.apn')
        self.assertEqual(slot2['apn'], 'backup.internet')
