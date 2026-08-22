# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class FailoverArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the failover module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "enabled": {
                    "type": "bool",
                },
                "probe_physif": {
                    "type": "str",
                    "description": (
                        "Interface through which the device probes probe_address. "
                        "Required when failover is enabled."
                    ),
                },
                "probe_address": {
                    "type": "str",
                    "description": "Primary probe address: IPv4/IPv6 address or hostname.",
                },
                "probe_address_2": {
                    "type": "str",
                    "description": (
                        "Secondary probe address. Probed if probe_address is unreachable. "
                        "A failover event occurs if this address is also unreachable."
                    ),
                },
                "dormant_dns": {
                    "type": "bool",
                    "description": (
                        "Whether DNS is dormant on the failover interface during normal operation. "
                        "DNS is restored during failover."
                    ),
                },
                "failover_physif": {
                    "type": "str",
                    "description": (
                        "Interface to fail over to. Defaults to wwan0 when failover is enabled "
                        "and this field is omitted."
                    ),
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
                "gathered",
                "rendered",
            ],
        },
    }  # pylint: disable=C0301
