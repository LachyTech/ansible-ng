# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.opengear.ng.plugins.module_utils.argspec.physifs import PhysifsArgs
from ansible_collections.opengear.ng.plugins.module_utils.utils import utils

# API-only fields that are never user-configurable
_READONLY_TOP = frozenset({"runtime_status", "mac_address", "master"})
_READONLY_ETHERNET = frozenset({"id", "available_link_speeds"})
_READONLY_CELLULAR = frozenset({"id", "available_carrier_firmwares"})
_READONLY_SIM = frozenset({"id", "runtime_status"})

# Map media type to its settings key — only include the matching one
_MEDIA_SETTING_KEY = {
    "ethernet": "ethernet_setting",
    "cellular": "cellular_setting",
    "bond": "bond_setting",
    "bridge": "bridge_setting",
    "vlan": "vlan_setting",
}

_ALL_SETTING_KEYS = frozenset(_MEDIA_SETTING_KEY.values())


class PhysifsFacts(object):
    """
    Retrieves and parses physical interface configuration facts from Opengear devices.
    """

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = PhysifsArgs.argument_spec
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
        return connection.get(None, "physifs")["physifs"]

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for physifs
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """

        if not data:
            data = self.get_device_data(connection)

        objs = []
        for instance in data:
            if instance:
                obj = self.render_config(self.generated_spec, instance)
                if obj:
                    objs.append(obj)
        ansible_facts["ansible_network_resources"].pop("physifs", None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {"config": objs})
            facts["physifs"] = params["config"]

        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render a physif API response as a config dict, stripping read-only
        sub-fields and excluding media-specific settings that don't apply to
        the interface's media type.
        """
        media = conf.get("media")
        applicable_setting = _MEDIA_SETTING_KEY.get(media)
        config = {}

        for key, value in conf.items():
            if key in _READONLY_TOP:
                continue
            # Only include the settings block that matches this interface's media type
            if key in _ALL_SETTING_KEYS and key != applicable_setting:
                continue

            if key == "ethernet_setting" and isinstance(value, dict):
                filtered = {
                    k: v for k, v in value.items() if k not in _READONLY_ETHERNET
                }
                config[key] = filtered
            elif key == "cellular_setting" and isinstance(value, dict):
                filtered = {
                    k: v for k, v in value.items() if k not in _READONLY_CELLULAR
                }
                if "sims" in filtered and isinstance(filtered["sims"], list):
                    filtered["sims"] = [
                        {k: v for k, v in sim.items() if k not in _READONLY_SIM}
                        for sim in filtered["sims"]
                    ]
                config[key] = filtered
            else:
                config[key] = value

        return utils.remove_empties(config)
