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
module: ports_power
version_added: '1.0.0'
short_description: Issues power commands to serial ports on Opengear devices
description:
  - Sends power on, off, or cycle commands to one or more serial ports.
  - This is an action module — it is always reported as changed when commands
    are issued. Use check mode to preview commands without sending them.
  - Ports must have a PDU outlet association configured for power commands
    to take effect on the connected device.
notes:
  - Power commands are not idempotent by nature. Each run sends the command
    to the device regardless of current state.
author:
  - Opengear (@opengear)
options:
  config:
    description: List of ports and the power command to issue to each.
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
      command:
        description: The power command to issue.
        type: str
        required: true
        choices: [on, off, cycle]
"""

EXAMPLES = """
- name: Power cycle a single port
  opengear.ng.ports_power:
    config:
      - portnum: 1
        command: cycle

- name: Power off multiple ports
  opengear.ng.ports_power:
    config:
      - portnum: 3
        command: off
      - portnum: 4
        command: off

- name: Preview power commands without sending (check mode)
  opengear.ng.ports_power:
    config:
      - portnum: 1
        command: cycle
  check_mode: true
"""

RETURN = """
commands:
  description: The set of API commands that were (or would be) sent.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.ports_power import PortsPowerArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.ports_power import PortsPower


def main():
    """
    Main entry point for module execution.

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=PortsPowerArgs.argument_spec,
        supports_check_mode=True,
    )

    result = PortsPower(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
