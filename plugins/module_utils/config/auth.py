# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from copy import deepcopy

from ansible.module_utils.connection import ConnectionError

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase
from ansible_collections.opengear.ng.plugins.module_utils.facts.facts import Facts
from ansible_collections.opengear.ng.plugins.module_utils.utils.utils import (
    to_list,
    remove_empties,
)

_SENSITIVE = frozenset({"radiusPassword", "tacacsPassword", "ldapBindPassword"})
_SERVER_LISTS = frozenset(
    {
        "radiusAuthenticationServers",
        "radiusAccountingServers",
        "tacacsAuthenticationServers",
        "ldapAuthenticationServers",
    }
)


class Auth(ConfigBase):
    """
    Manages auth configuration for Opengear devices
    """

    gather_subset = ["!all", "!min"]
    gather_network_resources = ["auth"]

    def __init__(self, module):
        super(Auth, self).__init__(module)

    def get_auth_facts(self):
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources
        )
        auth_facts = facts["ansible_network_resources"].get("auth")
        if not auth_facts:
            return {}
        return auth_facts

    def _simulate_after(self, existing, commands):
        """Compute expected after state from commands without calling the API."""
        if self.state in ("replaced", "overridden"):
            # Full replacement: the command data IS the new state
            simulated = {}
            for command in commands:
                if command["method"] == "PUT" and command["data"]:
                    data = remove_empties(command["data"].get("auth", {}))
                    for sf in _SENSITIVE:
                        data.pop(sf, None)
                    simulated = data
        else:
            # Merged: start from existing, overlay command fields
            simulated = deepcopy(existing) if existing else {}
            for command in commands:
                if command["method"] == "PUT" and command["data"]:
                    data = remove_empties(command["data"].get("auth", {}))
                    for sf in _SENSITIVE:
                        data.pop(sf, None)
                    simulated.update(data)
        return simulated

    def execute_module(self):
        result = {"changed": False}
        warnings = list()
        commands = list()

        if self.state in self.ACTION_STATES:
            existing_auth_facts = self.get_auth_facts()
        else:
            existing_auth_facts = {}

        if self.state in self.ACTION_STATES or self.state == "rendered":
            commands.extend(self.set_config(existing_auth_facts))

        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    try:
                        self._connection.send_request(
                            command["data"], command["path"], command["method"]
                        )
                    except ConnectionError as exc:
                        if not exc.args[0].startswith("Expecting value:"):
                            raise exc
            result["changed"] = True

        result["commands"] = commands

        if self.state in self.ACTION_STATES or self.state == "gathered":
            if self._module.check_mode and result["changed"]:
                changed_auth_facts = self._simulate_after(existing_auth_facts, commands)
            else:
                changed_auth_facts = self.get_auth_facts()
        elif self.state == "rendered":
            result["rendered"] = commands

        if self.state in self.ACTION_STATES:
            result["before"] = existing_auth_facts
            if result["changed"]:
                result["after"] = changed_auth_facts
                if self._module._diff:
                    simulated = self._simulate_after(existing_auth_facts, commands)
                    result["diff"] = {
                        "before": json.dumps(existing_auth_facts or {}, indent=4)
                        + "\n",
                        "after": json.dumps(simulated, indent=4) + "\n",
                    }
        elif self.state == "gathered":
            result["gathered"] = changed_auth_facts

        result["warnings"] = warnings
        return result

    def set_config(self, existing_auth_facts):
        want = self._module.params["config"]
        have = existing_auth_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        state = self._module.params["state"]
        if state in ("overridden", "replaced"):
            return self._state_replaced(want, have)
        elif state == "merged":
            return self._state_merged(want, have)
        return []

    @staticmethod
    def _state_replaced(want, have):
        want = remove_empties(want)
        have = remove_empties(have)
        has_sensitive = any(k in want for k in _SENSITIVE)
        want_compare = {k: v for k, v in want.items() if k not in _SENSITIVE}
        have_compare = {k: v for k, v in have.items() if k not in _SENSITIVE}
        if want_compare != have_compare or has_sensitive:
            return [{"data": {"auth": want}, "path": "auth", "method": "PUT"}]
        return []

    @staticmethod
    def _state_merged(want, have):
        want = remove_empties(want)
        have = remove_empties(have)
        merged = {**have, **want}
        has_skip = any(k in want for k in _SENSITIVE | _SERVER_LISTS)
        merged_compare = {
            k: v for k, v in merged.items() if k not in (_SENSITIVE | _SERVER_LISTS)
        }
        have_compare = {
            k: v for k, v in have.items() if k not in (_SENSITIVE | _SERVER_LISTS)
        }
        if merged_compare != have_compare or has_skip:
            return [{"data": {"auth": merged}, "path": "auth", "method": "PUT"}]
        return []
