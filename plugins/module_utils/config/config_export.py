# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase
from ansible_collections.opengear.ng.plugins.module_utils.facts.config_export import ConfigExportFacts


class ConfigExport(ConfigBase):
    """
    Retrieves device configuration export from Opengear devices.
    """

    gather_subset = ['!all', '!min']
    gather_network_resources = ['config_export']

    def __init__(self, module):
        super(ConfigExport, self).__init__(module)

    def get_config_export_facts(self):
        """Get the current device configuration export.

        :rtype: str
        :returns: The device configuration in dotnotation format
        """
        ansible_facts = {'ansible_network_resources': {}}
        # Use standalone facts for config export
        instance = ConfigExportFacts(self._module)
        instance.populate_facts(self._connection, ansible_facts)
        return ansible_facts['ansible_network_resources'].get('config_export')

    def execute_module(self):
        """Execute the module.

        :rtype: dict
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()

        result['gathered'] = self.get_config_export_facts()
        result['warnings'] = warnings
        return result
