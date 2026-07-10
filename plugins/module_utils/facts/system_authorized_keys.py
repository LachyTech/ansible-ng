# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.opengear.ng.plugins.module_utils.utils import utils
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_authorized_keys import (
    SystemAuthorizedKeysArgs,
)


class SystemAuthorizedKeysFacts(object):
    """ The system_authorized_keys facts class """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = SystemAuthorizedKeysArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_device_data(self, connection):
        """ Fetch the system-level authorized keys collection. """
        return connection.get(None, 'system/system_authorized_keys', query_params=None).get('system_authorized_keys', [])

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for system_authorized_keys

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if data is None:
            data = self.get_device_data(connection)

        objs = []
        for record in data:
            # Preserve id and key string for DELETE path resolution.
            # key_fingerprint is informational only and is not returned.
            obj = {
                'id': record.get('id'),
                'username': record.get('username'),
                'key': record.get('key'),
            }
            if record.get('multi_field_identifier'):
                obj['multi_field_identifier'] = record['multi_field_identifier']
            objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('system_authorized_keys', None)
        facts = {}
        if objs:
            facts['system_authorized_keys'] = objs

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts
