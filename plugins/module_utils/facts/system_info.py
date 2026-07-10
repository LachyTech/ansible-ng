# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class SystemInfoFacts(object):
    """
    Retrieves read-only system information facts from the system/info endpoint.
    """

    def __init__(self, module):
        self._module = module

    def get_device_data(self, connection):
        return connection.get(None, 'system/info')['system_info']

    def populate_facts(self, connection, ansible_facts, data=None):
        if not data:
            data = self.get_device_data(connection)

        ansible_facts['ansible_network_resources'].pop('system_info', None)
        if data:
            ansible_facts['ansible_network_resources']['system_info'] = data
        return ansible_facts
