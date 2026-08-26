# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy
import json

from ansible.module_utils.connection import ConnectionError

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase
from ansible_collections.opengear.ng.plugins.module_utils.facts.facts import Facts
from ansible_collections.opengear.ng.plugins.module_utils.utils.utils import (
    command_builder,
    dict_merge,
    find_instance_id,
    is_subset,
    remove_empties,
    to_list,
)

# id and name are identifier-only fields — the device auto-assigns name on POST
_BODY_EXCLUDE = frozenset({"id", "name"})


def _strip_body_fields(data):
    return {k: v for k, v in data.items() if k not in _BODY_EXCLUDE}


def _find_conn_by_ip(data, id_conn_map):
    """Find an existing conn by IP address when name/id lookup fails.

    The device auto-assigns conn names on POST so name-based lookup fails on
    subsequent runs.  Matching by static IP address provides a stable fallback
    identity that survives device renames.
    """
    target_v4 = (data.get("ipv4_static_settings") or {}).get("address")
    target_v6 = (data.get("ipv6_static_settings") or {}).get("address")
    if not target_v4 and not target_v6:
        return None
    for conn_id, conn in id_conn_map.items():
        if target_v4 and (conn.get("ipv4_static_settings") or {}).get("address") == target_v4:
            return conn_id
        if target_v6 and (conn.get("ipv6_static_settings") or {}).get("address") == target_v6:
            return conn_id
    return None


class Conns(ConfigBase):
    """
    Manages network connection configuration for Opengear devices
    """

    gather_subset = [
        "!all",
        "!min",
    ]

    gather_network_resources = [
        "conns",
    ]

    def __init__(self, module):
        super(Conns, self).__init__(module)
        self.current_state = {}

    def get_conns_facts(self, data=None):
        """Get the 'facts' (the current configuration)

        :rtype: A list
        :returns: The current configuration as a list
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources, data
        )
        conns_facts = facts["ansible_network_resources"].get("conns")
        if not conns_facts:
            return []
        return conns_facts

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {"changed": False}
        warnings = list()
        commands = list()

        if self.state in self.ACTION_STATES:
            existing_conns_facts = self.get_conns_facts()
        else:
            existing_conns_facts = {}

        if self.state in self.ACTION_STATES or self.state == "rendered":
            commands.extend(self.set_config(existing_conns_facts, warnings))

        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    conn_id = None
                    if command["method"] in ["PUT", "DELETE"]:
                        conn_id = command["path"].split("/")[-1]
                    try:
                        response = self._connection.send_request(
                            command["data"], command["path"], command["method"]
                        )
                        if command["method"] == "DELETE":
                            self.current_state.pop(conn_id, None)
                        elif conn_id and command["method"] == "PUT":
                            self.current_state[conn_id] = response.get("conn", {})
                        else:
                            created = response.get("conn", {})
                            created_id = created.get("id")
                            if created_id:
                                self.current_state[created_id] = created
                    except ConnectionError as exc:
                        if not exc.args[0].startswith("Expecting value:"):
                            raise exc
                        if conn_id:
                            self.current_state.pop(conn_id, None)
            else:
                # Simulate state changes for check mode + diff
                for command in commands:
                    if command["method"] == "DELETE":
                        conn_id = command["path"].split("/")[-1]
                        self.current_state.pop(conn_id, None)
                    elif command["method"] == "PUT":
                        conn_id = command["path"].split("/")[-1]
                        if conn_id in self.current_state:
                            self.current_state[conn_id].update(command["data"]["conn"])
                    elif command["method"] == "POST":
                        data = command["data"]["conn"]
                        temp_key = "check-{0}".format(data.get("name", "new"))
                        self.current_state[temp_key] = data
            result["changed"] = True

        result["commands"] = commands

        if self.state in self.ACTION_STATES or self.state == "gathered":
            changed_conns_facts = self.get_conns_facts(self.current_state.values())
        elif self.state == "rendered":
            result["rendered"] = commands

        if self.state in self.ACTION_STATES:
            result["before"] = existing_conns_facts
            if result["changed"]:
                result["after"] = changed_conns_facts
                if self._module._diff:
                    diff_before = []
                    diff_after = []
                    existing_by_id = {
                        c["id"]: c for c in existing_conns_facts if c.get("id")
                    }

                    for command in commands:
                        if command["method"] == "DELETE":
                            conn_id = command["path"].split("/")[-1]
                            if conn_id in existing_by_id:
                                diff_before.append(existing_by_id[conn_id])
                                diff_after.append({})
                        elif command["method"] == "PUT":
                            conn_id = command["path"].split("/")[-1]
                            if conn_id in existing_by_id:
                                before = existing_by_id[conn_id]
                                after = {**before, **command["data"]["conn"]}
                                diff_before.append(before)
                                diff_after.append(after)
                        elif command["method"] == "POST":
                            diff_before.append({})
                            diff_after.append(command["data"]["conn"])

                    result["diff"] = {
                        "before": json.dumps(diff_before, indent=4) + "\n",
                        "after": json.dumps(diff_after, indent=4) + "\n",
                    }
        elif self.state == "gathered":
            result["gathered"] = changed_conns_facts

        result["warnings"] = warnings
        return result

    def set_config(self, existing_conns_facts, warnings):
        """Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params["config"]
        have = existing_conns_facts
        resp = self.set_state(want, have, warnings)
        return to_list(resp)

    def set_state(self, want, have, warnings):
        """Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        name_id_map = {}
        id_conn_map = {}
        for conn in have:
            if conn.get("name") and conn.get("id"):
                name_id_map[conn["name"]] = conn["id"]
            if conn.get("id"):
                id_conn_map[conn["id"]] = conn

        self.current_state = deepcopy(id_conn_map)

        warned = set()
        for conn in want or []:
            for settings_key in ("ipv4_static_settings", "ipv6_static_settings"):
                settings = (conn or {}).get(settings_key) or {}
                for field in ("dns1", "dns2"):
                    if settings.get(field):
                        msg = (
                            "opengear.ng.conns: '{0}.{1}' is deprecated since 10/2021; "
                            "use opengear.ng.physifs 'dns.nameservers' instead".format(
                                settings_key, field
                            )
                        )
                        if msg not in warned:
                            warned.add(msg)
                            warnings.append(msg)

        state = self._module.params["state"]
        if state == "overridden":
            commands = self._state_overridden(want, name_id_map, id_conn_map)
        elif state == "deleted":
            commands = self._state_deleted(want, name_id_map, id_conn_map)
        elif state == "merged":
            commands = self._state_merged(want, name_id_map, id_conn_map)
        elif state == "replaced":
            commands = self._state_replaced(want, name_id_map, id_conn_map)
        else:
            commands = []
        return commands

    @staticmethod
    def _state_replaced(want, name_id_map, id_conn_map):
        """The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to set the desired configuration,
                  replacing the full config of each matched conn
        """
        commands = []
        for conn in want:
            conn = deepcopy(conn)
            conn_id = find_instance_id(name_id_map, "name", conn)
            data = remove_empties(conn)
            if conn_id is None:
                conn_id = _find_conn_by_ip(data, id_conn_map)
            if conn_id in id_conn_map:
                have_clean = _strip_body_fields(remove_empties(id_conn_map[conn_id]))
                want_clean = _strip_body_fields(data)
                if is_subset(want_clean, have_clean):
                    continue
            body = _strip_body_fields(data)
            command = command_builder({"conn": body}, "conns/", conn_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_overridden(want, name_id_map, id_conn_map):
        """The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to set exactly the desired conns,
                  deleting any conns not in want
        """
        commands = []
        deleted_conns = deepcopy(id_conn_map)

        for conn in want:
            conn_copy = deepcopy(conn)
            if conn_copy.get("id") and conn_copy["id"] in id_conn_map:
                conn_id = conn_copy["id"]
            else:
                conn_id = find_instance_id(deepcopy(name_id_map), "name", conn_copy)
            if conn_id in deleted_conns:
                deleted_conns.pop(conn_id)

        commands.extend(
            Conns._state_deleted(list(deleted_conns.values()), name_id_map, id_conn_map)
        )
        commands.extend(Conns._state_replaced(want, name_id_map, id_conn_map))
        return commands

    @staticmethod
    def _state_merged(want, name_id_map, id_conn_map):
        """The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided config into
                  the current configuration
        """
        commands = []
        for conn in want:
            conn = deepcopy(conn)
            data = remove_empties(conn)
            conn_id = find_instance_id(name_id_map, "name", data)

            if conn_id is None:
                conn_id = _find_conn_by_ip(data, id_conn_map)

            if conn_id in id_conn_map:
                have_clean = _strip_body_fields(remove_empties(id_conn_map[conn_id]))
                want_clean = _strip_body_fields(data)
                if is_subset(want_clean, have_clean):
                    continue
                # Deep-merge into device state so unspecified fields are preserved
                body = dict_merge(deepcopy(have_clean), want_clean)
            else:
                conn_id = None
                body = _strip_body_fields(data)

            command = command_builder({"conn": body}, "conns/", conn_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_deleted(want, name_id_map, id_conn_map):
        """The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to delete the specified conns
        """
        commands = []
        for conn in want:
            conn = deepcopy(conn)
            data = remove_empties(conn)
            conn_id = find_instance_id(name_id_map, "name", conn)
            if conn_id is None:
                conn_id = _find_conn_by_ip(data, id_conn_map)
            if not conn_id or conn_id not in id_conn_map:
                continue
            command = command_builder(None, "conns/", conn_id)
            if command:
                commands.append(command)
        return commands
