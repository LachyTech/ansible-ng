#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'opengear'
}

DOCUMENTATION = """
---
module: ports_sessions
version_added: '1.0.0'
short_description: Terminates active pmshell sessions on serial ports
description:
  - Terminates active pmshell sessions on one or more serial ports.
  - Idempotent — if no matching sessions exist, no change is reported.
  - Specific sessions can be targeted by C(client_pid). If C(client_pid) is
    omitted, all active sessions on the port are terminated.
  - Use M(opengear.ng.ports_status) to inspect current sessions before acting.
author:
  - Opengear (@opengear)
options:
  config:
    description: List of ports (and optionally specific session PIDs) to terminate.
    type: list
    elements: dict
    required: true
    suboptions:
      id:
        description: The API ID of the port (e.g. C(ports-1)).
        type: str
      portnum:
        description: The physical port number. Preferred identifier.
        type: int
      name:
        description: The system-assigned port name (e.g. C(port01)).
        type: str
      client_pid:
        description: >
          Specific pmshell session PIDs to terminate. If omitted, all active
          sessions on the port are terminated.
        type: list
        elements: int
"""

EXAMPLES = """
- name: Terminate all sessions on port 2
  opengear.ng.ports_sessions:
    config:
      - portnum: 2

- name: Terminate a specific session by PID
  opengear.ng.ports_sessions:
    config:
      - portnum: 2
        client_pid:
          - 12345

- name: Terminate all sessions across multiple ports
  opengear.ng.ports_sessions:
    config:
      - portnum: 1
      - portnum: 3
      - portnum: 5

- name: Check what sessions would be terminated (check mode)
  opengear.ng.ports_sessions:
    config:
      - portnum: 2
  check_mode: true
"""

RETURN = """
commands:
  description: The set of API commands that were (or would be) sent.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.ports_sessions import PortsSessionsArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.ports_sessions import PortsSessions


def main():
    """
    Main entry point for module execution.

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=PortsSessionsArgs.argument_spec,
        supports_check_mode=True,
    )

    result = PortsSessions(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
