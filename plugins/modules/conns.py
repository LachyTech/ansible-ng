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



EXAMPLES = """
- name: Configure a network connection
  opengear.ng.conns:
    config:
      - description: static-ipv4-net1
        mode: static
        physif: net1
        ipv4_static_settings:
          netmask: "255.255.255.0"
          address: "192.168.1.2"
          broadcast: "192.168.1.255"
          gateway: "192.168.1.1"
      - description: dynamic-ipv6-net1
        mode: ipv6_automatic
        physif: net1
    state: merged

- name: Gather connection facts
  opengear.ng.facts:
    gather_network_resources:
      - conns
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.conns import ConnsArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.conns import Conns


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=ConnsArgs.argument_spec,
                           supports_check_mode=True)

    result = Conns(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
