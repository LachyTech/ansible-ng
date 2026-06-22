#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
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
module: groups
version_added: '1.0.0'
short_description: Manages configuration of groups on Opengear devices
description:
  - Manages configuration of groups on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of groups on Opengear devices
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description: A unique identifier for this group.
      groupname:
        type: str
        description: The POSIX name for the group. (maxLength: 60)
      description:
        type: str
        description: A description of the group's purpose. (maxLength: 128)
      enabled:
        type: bool
        description: >
          If the group is currently enabled.
          If a group is disabled, any permissions attached to it will not be bestowed upon users in that group.
      access_rights:
        type: list
        elements: str
        description: A list of resources or features that members of this group have been granted access to.
      members:
        type: list
        elements: str
        description: >
          A list of users assigned to this group.
          The users can be referenced by either usernames or user ids.
      ports:
        type: list
        elements: str
        description: A list of port ids that users in this group can access.
      mode:
        type: str
        description: >
          Set to global to allow access to all ports.
          Set to scoped to limit access to specific ports.
        deprecated:
          removed_in: "1.0.0"
          why: Fine-grained C(access_rights) replaced mode/role permissions in 2022/08.
          alternative: access_rights
      role:
        type: str
        description: >
          Set to Administrator to allow access to the entire web UI.
          Set to ConsoleUser to limit access to serial port pages only.
        deprecated:
          removed_in: "1.0.0"
          why: Fine-grained C(access_rights) replaced mode/role permissions in 2022/08.
          alternative: access_rights
  state:
    description:
    - The state of the configuration after module completion.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - gathered
    - rendered
    default: merged
notes:
  - Diff output shows the expected configuration change based on the commands
    generated. It does not reflect the actual device state after execution,
    which may differ due to device-side normalization or concurrent changes.
    Use state=gathered after a run to verify the actual device state.
"""

EXAMPLES = """
- name: Configure groups
  opengear.ng.groups:
    config:
      - groupname: netops
        description: Network operations group
        enabled: true
        access_rights:
          - admin
      - groupname: readonly
        description: Read only group
        enabled: true
        access_rights:
          - web_ui
          - pmshell
        ports:
          - ports-1
          - ports-2
    state: merged

- name: Delete a group
  opengear.ng.groups:
    config:
      - groupname: readonly
    state: deleted

- name: Gather group facts
  opengear.ng.facts:
    gather_network_resources:
      - groups
"""

RETURN = """
before:
  description: The configuration before the module is executed.
  returned: always
  type: dict
after:
  description: The configuration after the module is executed.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.groups import GroupsArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.groups import Groups


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=GroupsArgs.argument_spec,
                           supports_check_mode=True)

    result = Groups(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
