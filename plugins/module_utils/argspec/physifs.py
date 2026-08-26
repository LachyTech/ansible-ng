# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class PhysifsArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the physifs module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "id": {"type": "str"},
                "name": {"type": "str"},
                "enabled": {"type": "bool"},
                "description": {"type": "str"},
                "media": {
                    "type": "str",
                    "choices": [
                        "ethernet",
                        "cellular",
                        "bridge",
                        "bond",
                        "vlan",
                        "loopback",
                    ],
                },
                "mtu": {"type": "int"},
                "device": {"type": "str"},
                "slaves": {
                    "type": "list",
                    "elements": "str",
                },
                "dns": {
                    "type": "dict",
                    "options": {
                        "nameservers": {
                            "type": "list",
                            "elements": "str",
                        },
                        "search_domains": {
                            "type": "list",
                            "elements": "str",
                        },
                    },
                },
                "ethernet_setting": {
                    "type": "dict",
                    "options": {
                        "link_speed": {
                            "type": "str",
                            "choices": [
                                "auto",
                                "1000mbps-fd",
                                "100mbps-hd",
                                "100mbps-fd",
                                "10mbps-hd",
                                "10mbps-fd",
                            ],
                        },
                    },
                },
                "cellular_setting": {
                    "type": "dict",
                    "options": {
                        "active_sim": {"type": "int"},
                        "sim_failover_policy": {
                            "type": "str",
                            "choices": ["never", "on_disconnect"],
                        },
                        "sim_failover_disconnect_mode": {
                            "type": "str",
                            "choices": ["ping"],
                        },
                        "sim_failback_policy": {
                            "type": "str",
                            "choices": ["never", "delayed", "on_disconnect"],
                        },
                        "sim_failback_disconnect_mode": {
                            "type": "str",
                            "choices": ["ping"],
                        },
                        "sims": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "slot": {"type": "int"},
                                "apn": {"type": "str"},
                                "username": {"type": "str"},
                                "password": {"type": "str", "no_log": True},
                                "iptype": {
                                    "type": "str",
                                    "choices": ["IPv4", "IPv6", "IPv4v6"],
                                },
                                "authtype": {
                                    "type": "str",
                                    "choices": ["none", "pap", "chap", "pap-chap"],
                                },
                                "ipv4_netmask": {"type": "str"},
                                "mtu": {"type": "int"},
                                "carrier_firmware": {"type": "str"},
                                "failback_delay": {"type": "int"},
                                "fail_probe_address": {"type": "str"},
                                "fail_probe_interval": {"type": "int"},
                                "fail_probe_count": {"type": "int"},
                                "fail_probe_threshold": {"type": "int"},
                            },
                        },
                    },
                },
                "bond_setting": {
                    "type": "dict",
                    "options": {
                        "mode": {
                            "type": "str",
                            "choices": [
                                "balance-rr",
                                "active-backup",
                                "balance-xor",
                                "broadcast",
                                "802.3ad",
                                "balance-tlb",
                                "balance-alb",
                            ],
                        },
                        "poll_interval": {"type": "int"},
                        "primary_slave": {"type": "str"},
                    },
                },
                "bridge_setting": {
                    "type": "dict",
                    "options": {
                        "stp_enabled": {"type": "bool"},
                        "primary_slave": {"type": "str"},
                    },
                },
                "vlan_setting": {
                    "type": "dict",
                    "options": {
                        "parent_physif": {"type": "str"},
                        "vlan_id": {"type": "int"},
                    },
                },
            },
        },
        "state": {
            "type": "str",
            "default": "merged",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
            ],
        },
    }  # pylint: disable=C0301
