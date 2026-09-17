# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.opengear.ng.plugins.module_utils.argspec.local_password_policy import (
    LocalPasswordPolicyArgs,
)
from ansible_collections.opengear.ng.plugins.module_utils.utils import utils


class LocalPasswordPolicyFacts(object):
    """
    Retrieves and parses local password policy configuration facts from Opengear devices.
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = LocalPasswordPolicyArgs.argument_spec
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
        return connection.get(None, 'local_password_policy')['local_password_policy']

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for local_password_policy
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """

        if not data:
            data = self.get_device_data(connection)

        obj = {}
        if data:
            obj.update(self.render_config(self.generated_spec, data))

        ansible_facts['ansible_network_resources'].pop('local_password_policy', None)
        facts = {}
        if obj:
            params = utils.validate_config(self.argument_spec, {'config': obj})
            facts['local_password_policy'] = params['config']
        else:
            facts['local_password_policy'] = {}

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        for option in config.keys():
            if option in conf:
                config[option] = conf[option]
        return utils.remove_empties(config)
