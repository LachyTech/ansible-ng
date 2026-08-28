# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.connection import ConnectionError

from ansible_collections.opengear.ng.plugins.module_utils.utils import utils


class SingletonFacts(object):
    """
    Base class for retrieving *singleton* system resource facts from Opengear
    devices. Each field is fetched from its own REST endpoint and unwrapped
    through its body path (see ``SingletonConfigBase`` for the field map
    contract).

    Subclasses declare:
      * ``resource_name`` - the ansible_network_resources key.
      * ``args`` - the argspec class describing the resource.
      * ``field_map`` - ``{config_field: (endpoint, [body_path...])}``.
      * ``gather_exclude`` - fields present in ``field_map`` (so they can be
        *written*) but which must not be fetched or returned as facts, e.g.
        non-idempotent values like the device clock whose momentary reading
        would only produce noise in ``gathered``/``before``/``after``.
    """

    resource_name = None
    args = None
    field_map = {}
    gather_exclude = ()
    # Fields that may not be present on all hardware; silently omitted on
    # ConnectionError rather than failing the entire gather.
    optional_fields = ()

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = self.args.argument_spec
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
        """ Fetch each gatherable field's raw (wrapped) body from its endpoint. """
        data = {}
        for field, (endpoint, _body_path) in self.field_map.items():
            if field in self.gather_exclude:
                continue
            if field in self.optional_fields:
                try:
                    data[field] = connection.get(None, endpoint)
                except ConnectionError:
                    pass
            else:
                data[field] = connection.get(None, endpoint)
        return data

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for this resource
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
            obj = self.render_config(self.generated_spec, data)

        ansible_facts['ansible_network_resources'].pop(self.resource_name, None)
        facts = {}
        if obj:
            params = utils.validate_config(self.argument_spec, {'config': obj})
            facts[self.resource_name] = params['config']
        else:
            facts[self.resource_name] = {}

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as a dictionary, unwrapping each field's value from its
        REST body path and dropping empty values.

        :param spec: The facts tree, generated from the argspec
        :param conf: The raw device data keyed by config field
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        for field, (_endpoint, body_path) in self.field_map.items():
            if field in self.gather_exclude:
                config.pop(field, None)
                continue
            if field not in conf:
                continue
            value = conf[field]
            for key in body_path:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            config[field] = value
        return utils.remove_empties(config)
