# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import ports_status
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestPortsStatusModule(TestModuleBase):

    module = ports_status

    def setUp(self):
        super(TestPortsStatusModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.ports_status.PortsStatusFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestPortsStatusModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("ports_config.cfg")

    def test_gathered_returns_all_ports(self):
        """Gathered status includes every port on the device."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        self.assertEqual(len(result['gathered']), 4)

    def test_gathered_includes_core_identity_fields(self):
        """Each entry surfaces id, name, portnum, mode, device, and status."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        port1 = next(p for p in result['gathered'] if p['portnum'] == 1)
        self.assertEqual(port1['id'], 'ports-1')
        self.assertEqual(port1['name'], 'port01')
        self.assertEqual(port1['mode'], 'consoleServer')
        self.assertEqual(port1['device'], 'serial/by-opengear-id/port01')
        self.assertEqual(port1['status'], 'ok')

    def test_gathered_session_fields_filtered(self):
        """Fields outside username/client_pid are stripped from session data."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        port2 = next(p for p in result['gathered'] if p['portnum'] == 2)
        self.assertEqual(port2['sessions'], [{'username': 'admin', 'client_pid': 12345}])
        self.assertNotIn('tty', port2['sessions'][0])

    def test_gathered_includes_pdu_outlets(self):
        """PDU outlet associations are surfaced when present."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        port4 = next(p for p in result['gathered'] if p['portnum'] == 4)
        self.assertEqual(port4['pdu_outlets'], ['pdu-1-outlet-1'])

    def test_gathered_empty_sessions_and_pdu_outlets_retained(self):
        """Empty sessions/pdu_outlets lists are kept, not stripped."""
        set_module_args({'state': 'gathered'})
        result = self.execute_module(changed=False)
        port1 = next(p for p in result['gathered'] if p['portnum'] == 1)
        self.assertEqual(port1['sessions'], [])
        self.assertEqual(port1['pdu_outlets'], [])

    def test_gathered_never_changes_device(self):
        """This module never reports changed, regardless of device state."""
        set_module_args({'state': 'gathered'})
        self.execute_module(changed=False)
        self.connection.return_value.send_request.assert_not_called()
