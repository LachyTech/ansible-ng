# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import ports_sessions
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestPortsSessionsModule(TestModuleBase):

    module = ports_sessions

    def setUp(self):
        super(TestPortsSessionsModule, self).setUp()
        self.maxDiff = None

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestPortsSessionsModule, self).tearDown()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        ports = load_fixture("ports_config.cfg")

        def send_request_side_effect(data, path, method=None):
            if path == 'ports' and data is None:
                return {'ports': ports}
            return {}

        self.connection.return_value.send_request.side_effect = send_request_side_effect

    def test_terminate_all_sessions_on_port(self):
        """Omitting client_pid terminates every session on the port."""
        set_module_args({'config': [{'portnum': 2}]})
        commands = [
            {'data': None, 'path': 'ports/ports-2/sessions/', 'method': 'DELETE'}
        ]
        self.execute_module(changed=True, commands=commands)

    def test_terminate_specific_existing_pid(self):
        """A client_pid that matches an active session is terminated."""
        set_module_args({'config': [{'portnum': 2, 'client_pid': [12345]}]})
        commands = [
            {'data': None, 'path': 'ports/ports-2/sessions/12345', 'method': 'DELETE'}
        ]
        self.execute_module(changed=True, commands=commands)

    def test_terminate_nonexistent_pid_is_idempotent(self):
        """A client_pid with no matching session produces no command."""
        set_module_args({'config': [{'portnum': 2, 'client_pid': [99999]}]})
        self.execute_module(changed=False, commands=[])

    def test_terminate_all_on_port_with_no_sessions_is_idempotent(self):
        """A port with no active sessions produces no command."""
        set_module_args({'config': [{'portnum': 1}]})
        self.execute_module(changed=False, commands=[])

    def test_multiple_ports_in_one_run(self):
        """Each entry in config is evaluated independently."""
        set_module_args({
            'config': [
                {'portnum': 1},
                {'portnum': 2},
            ],
        })
        # Port 1 has no sessions (idempotent), port 2 has one (terminated).
        commands = [
            {'data': None, 'path': 'ports/ports-2/sessions/', 'method': 'DELETE'}
        ]
        self.execute_module(changed=True, commands=commands)

    def test_resolves_by_name(self):
        """Ports can also be identified by their system-assigned name."""
        set_module_args({'config': [{'name': 'port02'}]})
        commands = [
            {'data': None, 'path': 'ports/ports-2/sessions/', 'method': 'DELETE'}
        ]
        self.execute_module(changed=True, commands=commands)

    def test_unresolved_port_skipped(self):
        """A portnum that does not exist on the device produces no command."""
        set_module_args({'config': [{'portnum': 99}]})
        self.execute_module(changed=False, commands=[])

    def test_check_mode_skips_delete(self):
        """In check mode the DELETE is not sent, but is still reported."""
        set_module_args({'_ansible_check_mode': True, 'config': [{'portnum': 2}]})
        commands = [
            {'data': None, 'path': 'ports/ports-2/sessions/', 'method': 'DELETE'}
        ]
        self.execute_module(changed=True, commands=commands)
        # Only the port lookup GET should have been made - no DELETE.
        self.assertEqual(self.connection.return_value.send_request.call_count, 1)
