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
    dict_diff,
    find_instance_id,
    is_subset,
    remove_empties,
    to_list,
)

# Fields that identify a physif but must not be sent in PUT/POST request bodies
_BODY_EXCLUDE = frozenset({"id", "name"})

# Only aggregate media types can be deleted via the API
_DELETABLE_MEDIA = frozenset({"bond", "bridge", "vlan"})


def _merge_cellular(have_cellular, want_cellular):
    """Merge cellular_setting dicts, merging sims by slot number."""
    if not have_cellular:
        return want_cellular
    result = deepcopy(have_cellular)
    for key, value in (want_cellular or {}).items():
        if key == "sims" and isinstance(value, list):
            have_sims_by_slot = {
                s.get("slot"): s
                for s in (have_cellular.get("sims") or [])
                if s.get("slot")
            }
            merged_sims = deepcopy(list(have_sims_by_slot.values()))
            for want_sim in value:
                slot = want_sim.get("slot")
                if slot in have_sims_by_slot:
                    idx = next(
                        i for i, s in enumerate(merged_sims) if s.get("slot") == slot
                    )
                    merged_sims[idx] = {**merged_sims[idx], **remove_empties(want_sim)}
                else:
                    merged_sims.append(remove_empties(want_sim))
            result["sims"] = merged_sims
        else:
            result[key] = value
    return result


def _strip_body_fields(data):
    """Remove identifier-only fields that must not appear in API request bodies."""
    return {k: v for k, v in data.items() if k not in _BODY_EXCLUDE}


def _sims_equal(a_sims, b_sims):
    """Compare two SIM lists by slot, excluding passwords."""
    if len(a_sims) != len(b_sims):
        return False
    by_slot_a = {
        s.get("slot"): {k: v for k, v in s.items() if k != "password"} for s in a_sims
    }
    by_slot_b = {
        s.get("slot"): {k: v for k, v in s.items() if k != "password"} for s in b_sims
    }
    if set(by_slot_a.keys()) != set(by_slot_b.keys()):
        return False
    for slot, sim_a in by_slot_a.items():
        if dict_diff(sim_a, by_slot_b[slot]) or dict_diff(by_slot_b[slot], sim_a):
            return False
    return True


def _sims_subset(want_sims, have_sims):
    """Check if all SIM slots in want match corresponding slots in have, excluding passwords."""
    have_by_slot = {
        s.get("slot"): {k: v for k, v in s.items() if k != "password"}
        for s in (have_sims or [])
    }
    for want_sim in want_sims or []:
        slot = want_sim.get("slot")
        want_clean = {k: v for k, v in want_sim.items() if k != "password"}
        if slot not in have_by_slot:
            return False
        if not is_subset(want_clean, have_by_slot[slot]):
            return False
    return True


def _physif_diff(merged, device):
    """
    Compare two physif dicts for differences. Handles cellular_setting.sims
    as a slot-keyed list to avoid sorted(list_of_dicts) TypeError in dict_diff.
    """
    a = _strip_body_fields(deepcopy(merged))
    b = _strip_body_fields(deepcopy(device))
    a_cellular = a.pop("cellular_setting", None)
    b_cellular = b.pop("cellular_setting", None)

    diff = dict_diff(a, b)

    # Compare cellular separately: sims are list-of-dicts and cannot be sorted generically
    if a_cellular or b_cellular:
        a_sims = (a_cellular or {}).get("sims", [])
        b_sims = (b_cellular or {}).get("sims", [])
        a_flat = {k: v for k, v in (a_cellular or {}).items() if k != "sims"}
        b_flat = {k: v for k, v in (b_cellular or {}).items() if k != "sims"}
        if dict_diff(a_flat, b_flat) or not _sims_equal(a_sims, b_sims):
            diff["cellular_setting"] = a_cellular
    return diff


def _physif_is_subset(want, have):
    """
    Check whether want is a subset of have. Handles cellular_setting.sims
    as a slot-keyed list to avoid set(list_of_dicts) TypeError in is_subset.
    """
    a = _strip_body_fields(deepcopy(want))
    b = _strip_body_fields(deepcopy(have))
    a_cellular = a.pop("cellular_setting", None)
    b_cellular = b.pop("cellular_setting", None)

    if not is_subset(a, b):
        return False

    # Compare cellular separately
    if a_cellular:
        a_flat = {k: v for k, v in a_cellular.items() if k != "sims"}
        b_flat = {k: v for k, v in (b_cellular or {}).items() if k != "sims"}
        if not is_subset(a_flat, b_flat):
            return False
        if "sims" in a_cellular:
            if not _sims_subset(a_cellular["sims"], (b_cellular or {}).get("sims", [])):
                return False
    return True


class Physifs(ConfigBase):
    """
    Manages configuration of physical interfaces on Opengear devices
    """

    gather_subset = [
        "!all",
        "!min",
    ]

    gather_network_resources = [
        "physifs",
    ]

    def __init__(self, module):
        super(Physifs, self).__init__(module)
        self.current_state = {}

    def get_physifs_facts(self, data=None):
        """Get the 'facts' (the current configuration)

        :rtype: A list
        :returns: The current configuration as a list
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources, data
        )
        physifs_facts = facts["ansible_network_resources"].get("physifs")
        if not physifs_facts:
            return []
        return physifs_facts

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {"changed": False}
        warnings = list()
        commands = list()

        if self.state in self.ACTION_STATES:
            existing_physifs_facts = self.get_physifs_facts()
        else:
            existing_physifs_facts = {}

        if self.state in self.ACTION_STATES or self.state == "rendered":
            commands.extend(self.set_config(existing_physifs_facts, warnings))

        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    physif_id = None
                    if command["method"] in ["PUT", "DELETE"]:
                        physif_id = command["path"].split("/")[-1]
                    try:
                        response = self._connection.send_request(
                            command["data"], command["path"], command["method"]
                        )
                        if command["method"] == "DELETE":
                            self.current_state.pop(physif_id, None)
                        elif physif_id and command["method"] == "PUT":
                            self.current_state[physif_id] = response.get("physif", {})
                        else:
                            created = response.get("physif", {})
                            created_id = created.get("id")
                            if created_id:
                                self.current_state[created_id] = created
                    except ConnectionError as exc:
                        if not exc.args[0].startswith("Expecting value:"):
                            raise exc
                        if physif_id:
                            self.current_state.pop(physif_id, None)
            else:
                # Simulate state changes for check mode + diff
                for command in commands:
                    if command["method"] == "DELETE":
                        physif_id = command["path"].split("/")[-1]
                        self.current_state.pop(physif_id, None)
                    elif command["method"] == "PUT":
                        physif_id = command["path"].split("/")[-1]
                        if physif_id in self.current_state:
                            self.current_state[physif_id].update(
                                command["data"]["physif"]
                            )
                    elif command["method"] == "POST":
                        data = command["data"]["physif"]
                        temp_key = "check-{0}".format(data.get("device", "new"))
                        self.current_state[temp_key] = data
            result["changed"] = True

        result["commands"] = commands

        if self.state in self.ACTION_STATES or self.state == "gathered":
            changed_physifs_facts = self.get_physifs_facts(self.current_state.values())
        elif self.state == "rendered":
            result["rendered"] = commands

        if self.state in self.ACTION_STATES:
            result["before"] = existing_physifs_facts
            if result["changed"]:
                result["after"] = changed_physifs_facts
                if self._module._diff:
                    diff_before = []
                    diff_after = []
                    existing_by_id = {
                        p["id"]: p for p in existing_physifs_facts if p.get("id")
                    }

                    for command in commands:
                        if command["method"] == "DELETE":
                            physif_id = command["path"].split("/")[-1]
                            if physif_id in existing_by_id:
                                diff_before.append(existing_by_id[physif_id])
                                diff_after.append({})
                        elif command["method"] == "PUT":
                            physif_id = command["path"].split("/")[-1]
                            if physif_id in existing_by_id:
                                before = existing_by_id[physif_id]
                                after = {**before, **command["data"]["physif"]}
                                diff_before.append(before)
                                diff_after.append(after)
                        elif command["method"] == "POST":
                            diff_before.append({})
                            diff_after.append(command["data"]["physif"])

                    result["diff"] = {
                        "before": json.dumps(diff_before, indent=4) + "\n",
                        "after": json.dumps(diff_after, indent=4) + "\n",
                    }
        elif self.state == "gathered":
            result["gathered"] = changed_physifs_facts

        result["warnings"] = warnings
        return result

    def set_config(self, existing_physifs_facts, warnings):
        """Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params["config"]
        have = existing_physifs_facts
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
        id_physif_map = {}
        for physif in have:
            if physif.get("name") and physif.get("id"):
                name_id_map[physif["name"]] = physif["id"]
            if physif.get("id"):
                id_physif_map[physif["id"]] = physif

        self.current_state = deepcopy(id_physif_map)

        state = self._module.params["state"]
        if state == "overridden":
            commands = self._state_overridden(want, name_id_map, id_physif_map)
        elif state == "deleted":
            commands = self._state_deleted(want, name_id_map, id_physif_map)
        elif state == "merged":
            commands = self._state_merged(want, name_id_map, id_physif_map)
        elif state == "replaced":
            commands = self._state_replaced(want, name_id_map, id_physif_map)
        else:
            commands = []
        return commands

    @staticmethod
    def _state_replaced(want, name_id_map, id_physif_map):
        """The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to set the desired configuration,
                  replacing the full config of each matched physif
        """
        commands = []
        for physif in want:
            physif = deepcopy(physif)
            physif_id = find_instance_id(name_id_map, "name", physif)
            data = remove_empties(physif)
            if physif_id in id_physif_map:
                if _physif_is_subset(data, remove_empties(id_physif_map[physif_id])):
                    continue
            body = _strip_body_fields(data)
            command = command_builder({"physif": body}, "physifs/", physif_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_overridden(want, name_id_map, id_physif_map):
        """The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to set exactly the desired physifs,
                  deleting any aggregate physifs not in want
        """
        commands = []
        deleted_physifs = deepcopy(id_physif_map)

        for physif in want:
            physif = deepcopy(physif)
            physif_id = find_instance_id(deepcopy(name_id_map), "name", physif)
            if physif_id in deleted_physifs:
                deleted_physifs.pop(physif_id)

        commands.extend(
            Physifs._state_deleted(
                list(deleted_physifs.values()), name_id_map, id_physif_map
            )
        )
        commands.extend(Physifs._state_replaced(want, name_id_map, id_physif_map))
        return commands

    @staticmethod
    def _state_merged(want, name_id_map, id_physif_map):
        """The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided config into
                  the current configuration
        """
        commands = []
        for physif in want:
            physif = deepcopy(physif)
            physif_id = find_instance_id(name_id_map, "name", physif)
            data = remove_empties(physif)

            if physif_id in id_physif_map:
                device_physif = deepcopy(id_physif_map[physif_id])
                # Merge top-level fields, using slot-keyed merge for cellular sims
                merged = {
                    **device_physif,
                    **{k: v for k, v in data.items() if k != "cellular_setting"},
                }
                if "cellular_setting" in data:
                    merged["cellular_setting"] = _merge_cellular(
                        device_physif.get("cellular_setting"), data["cellular_setting"]
                    )
                if not _physif_diff(merged, device_physif):
                    continue
                data = merged
            else:
                physif_id = None

            body = _strip_body_fields(data)
            command = command_builder({"physif": body}, "physifs/", physif_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_deleted(want, name_id_map, id_physif_map):
        """The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to delete the specified physifs.
                  Only aggregate interfaces (bond, bridge, vlan) can be deleted.
        """
        commands = []
        for physif in want:
            physif = deepcopy(physif)
            physif_id = find_instance_id(name_id_map, "name", physif)
            if physif_id and physif_id in id_physif_map:
                media = id_physif_map[physif_id].get("media")
                if media not in _DELETABLE_MEDIA:
                    continue
            command = command_builder(None, "physifs/", physif_id)
            if command:
                commands.append(command)
        return commands
