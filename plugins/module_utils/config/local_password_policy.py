# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy
import json

from ansible.module_utils.connection import ConnectionError

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase
from ansible_collections.opengear.ng.plugins.module_utils.facts.facts import Facts
from ansible_collections.opengear.ng.plugins.module_utils.utils.utils import (
    dict_merge,
    is_subset,
    remove_empties,
    to_list,
)


class LocalPasswordPolicy(ConfigBase):
    """
    Manages configuration of the local password policy on Opengear devices
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'local_password_policy',
    ]

    def __init__(self, module):
        super(LocalPasswordPolicy, self).__init__(module)
        self.current_state = {}

    def get_local_password_policy_facts(self, data=None):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources, data
        )
        policy_facts = facts['ansible_network_resources'].get('local_password_policy')
        if not policy_facts:
            return {}
        return policy_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        if self.state in self.ACTION_STATES:
            existing_policy_facts = self.get_local_password_policy_facts()
        else:
            existing_policy_facts = {}

        if self.state in self.ACTION_STATES or self.state == 'rendered':
            commands.extend(self.set_config(existing_policy_facts))

        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    try:
                        self._connection.send_request(
                            command['data'], command['path'], command['method']
                        )
                    except ConnectionError as exc:
                        if not exc.args[0].startswith('Expecting value:'):
                            raise exc
            else:
                # Simulate state changes for check mode so result['after'] is accurate
                self.current_state = deepcopy(existing_policy_facts)
                for command in commands:
                    self.current_state.update(command['data']['local_password_policy'])
            result['changed'] = True

        result['commands'] = commands

        if self.state in self.ACTION_STATES or self.state == 'gathered':
            if result['changed'] and self._module.check_mode:
                # Use simulated state; device state is unchanged in check mode
                changed_policy_facts = self.get_local_password_policy_facts(self.current_state or None)
            else:
                changed_policy_facts = self.get_local_password_policy_facts()
        elif self.state == 'rendered':
            result['rendered'] = commands

        if self.state in self.ACTION_STATES:
            result['before'] = existing_policy_facts
            if result['changed']:
                result['after'] = changed_policy_facts
                if self._module._diff:
                    # Diff from the command body, so it's accurate in check mode too
                    cmd_body = commands[0]['data']['local_password_policy'] if commands else {}
                    diff_after = dict_merge(deepcopy(existing_policy_facts), cmd_body)
                    result['diff'] = {
                        'before': json.dumps(existing_policy_facts, indent=4) + '\n',
                        'after': json.dumps(diff_after, indent=4) + '\n',
                    }
        elif self.state == 'gathered':
            result['gathered'] = changed_policy_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_policy_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_policy_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        state = self._module.params['state']
        if state in ('merged', 'replaced', 'overridden'):
            commands = self._state_merged(want, have)
        else:
            commands = []
        return commands

    @staticmethod
    def _state_merged(want, have):
        """ The command generator for merged/replaced/overridden.

        The device requires every field on each PUT, so all three states
        merge want into have and send the full object.

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        want = remove_empties(want or {})
        have = remove_empties(have or {})
        if is_subset(want, have):
            return commands
        merged = dict_merge(have, want)
        commands.append({
            'data': {'local_password_policy': merged},
            'path': 'local_password_policy',
            'method': 'PUT',
        })
        return commands
