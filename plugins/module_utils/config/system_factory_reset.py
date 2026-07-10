# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.connection import ConnectionError

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase


class SystemFactoryReset(ConfigBase):
    """
    Erases the configuration of an Opengear appliance, restoring factory defaults.

    This is a destructive action rather than a stateful resource: there is no
    configuration to converge and no facts to gather. Running the module always
    issues a DELETE and always reports ``changed``. Under check mode the request
    is not sent.
    """

    def __init__(self, module):
        super(SystemFactoryReset, self).__init__(module)

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        command = {'data': None, 'path': 'system/config', 'method': 'DELETE'}
        result = {'changed': False, 'commands': [command], 'warnings': []}

        if not self._module.check_mode:
            try:
                self._connection.send_request(command['data'], command['path'], command['method'])
            except ConnectionError as exc:
                if not exc.args[0].startswith('Expecting value:'):
                    raise exc
        result['changed'] = True
        return result
