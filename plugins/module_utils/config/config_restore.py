# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase
from ansible_collections.opengear.ng.plugins.module_utils.facts.config_restore import ConfigRestoreFacts


class ConfigRestore(ConfigBase):
    """
    Manages configuration restore for Opengear devices.
    """

    gather_subset = ['!all', '!min']
    gather_network_resources = ['config_restore']

    def __init__(self, module):
        super(ConfigRestore, self).__init__(module)

    def get_config_restore_facts(self):
        """Get the current restore status.

        :rtype: dict
        :returns: The current restore status
        """
        ansible_facts = {'ansible_network_resources': {}}
        # Use standalone facts for config restore
        instance = ConfigRestoreFacts(self._module)
        instance.populate_facts(self._connection, ansible_facts)
        return ansible_facts['ansible_network_resources'].get('config_restore')

    def execute_module(self):
        """Execute the module.

        :rtype: dict
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()

        if self.state == 'gathered':
            result['gathered'] = self.get_config_restore_facts()
            result['warnings'] = warnings
            return result

        # replaced — initiate config restore
        want = self._module.params['config']

        if not want or not want.get('config_file'):
            self._module.fail_json(msg="config_file is required for state: replaced")

        if not self._module.check_mode:
            self._connection.send_multipart_request(
                'restore/config',
                file_path=want['config_file'],
            )
        result['changed'] = True
        result['warnings'] = warnings
        return result
