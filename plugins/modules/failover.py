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
module: failover
version_added: '1.0.0'
short_description: Manages configuration of failover behavior on Opengear devices
description:
  - Manages failover settings on Opengear devices.
  - The failover resource is a singleton — only one set of settings exists on the device.
  - C(replaced) and C(overridden) behave identically for this resource.
author:
  - Opengear (@opengear)
options:
  config:
    description: Desired failover configuration.
    type: dict
    suboptions:
      enabled:
        description: Enable or disable failover.
        type: bool
      probe_physif:
        description:
          - Network interface through which the device probes I(probe_address).
          - Required when failover is enabled.
        type: str
      probe_address:
        description: Primary probe address; an IPv4/IPv6 address or hostname.
        type: str
      probe_address_2:
        description:
          - Secondary probe address probed if I(probe_address) is unreachable.
          - A failover event occurs only if this address is also unreachable.
        type: str
      dormant_dns:
        description:
          - When C(true), DNS is suppressed on the failover interface during normal
            operation and restored when failover is active.
        type: bool
      failover_physif:
        description:
          - Interface to fail over to. Defaults to C(wwan0) on the device when
            failover is enabled and this field is omitted.
        type: str
  state:
    description:
      - The state of the configuration after module completion.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - gathered
      - rendered
    default: merged
"""

EXAMPLES = """
- name: Enable failover, probing 8.8.8.8 and 1.1.1.1 via net1, failing over to wwan0
  opengear.ng.failover:
    config:
      enabled: true
      probe_physif: net1
      probe_address: 8.8.8.8
      probe_address_2: 1.1.1.1
      failover_physif: wwan0
      dormant_dns: false
    state: merged

- name: Replace failover settings (sends only the specified fields)
  opengear.ng.failover:
    config:
      enabled: true
      probe_physif: net1
      probe_address: 8.8.8.8
      failover_physif: wwan0
    state: replaced

- name: Disable failover
  opengear.ng.failover:
    config:
      enabled: false
    state: merged

- name: Gather current failover settings
  opengear.ng.failover:
    state: gathered

- name: Gather failover facts via facts module
  opengear.ng.facts:
    gather_network_resources:
      - failover
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.failover import FailoverArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.failover import Failover


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=FailoverArgs.argument_spec,
                           supports_check_mode=True)

    result = Failover(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
