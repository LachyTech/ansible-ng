# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ConnsArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the conns module.
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
                "description": {"type": "str"},
                "mode": {
                    "type": "str",
                    "choices": ["static", "ipv6_static", "dhcp", "ipv6_automatic"],
                },
                "physif": {"type": "str"},
                "ipv4_static_settings": {
                    "type": "dict",
                    "options": {
                        "address": {"type": "str"},
                        "broadcast": {"type": "str"},
                        "dns1": {"type": "str"},
                        "dns2": {"type": "str"},
                        "gateway": {"type": "str"},
                        "netmask": {"type": "str"},
                    },
                },
                "ipv6_static_settings": {
                    "type": "dict",
                    "options": {
                        "address": {"type": "str"},
                        "dns1": {"type": "str"},
                        "dns2": {"type": "str"},
                        "gateway": {"type": "str"},
                        "prefix_length": {"type": "int"},
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
