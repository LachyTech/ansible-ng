# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class CollectionFacts(object):
    """
    Base class for retrieving *collection* resource facts from Opengear
    devices - id-keyed lists of records fetched from a single collection
    endpoint (see ``CollectionConfigBase`` for the CRUD counterpart).

    Subclasses declare:
      * ``resource_name`` - the ansible_network_resources key.
      * ``endpoint`` - the collection's REST path, e.g. ``services/syslog``.
      * ``list_key`` - the JSON body key the list is wrapped in, e.g.
        ``syslogServers``.
    """

    resource_name = None
    endpoint = None
    list_key = None

    def __init__(self, module):
        self._module = module

    def get_device_data(self, connection):
        """ Fetch the raw collection from its endpoint. """
        return connection.get(None, self.endpoint, query_params=None).get(self.list_key, [])

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for this resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if data is None:
            data = self.get_device_data(connection)

        ansible_facts['ansible_network_resources'].pop(self.resource_name, None)
        facts = {}
        if data:
            facts[self.resource_name] = data

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts
