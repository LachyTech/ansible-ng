# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.config_restore import ConfigRestoreArgs


class ConfigRestoreFacts(object):
    """
    Retrieves configuration restore status facts from Opengear devices.
    """

    def __init__(self, module):
        self._module = module
        self.argument_spec = ConfigRestoreArgs.argument_spec

    def get_device_data(self, connection):
        """Fetch the current restore status."""
        return connection.get(None, 'restore/config')

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for config_restore.

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_device_data(connection)

        ansible_facts['ansible_network_resources'].pop('config_restore', None)
        facts = {}
        if data:
            facts['config_restore'] = data

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts
