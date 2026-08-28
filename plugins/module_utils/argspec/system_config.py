# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class SystemArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the system_config module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "options": {
                "admin_info": {
                    "options": {
                        "contact": {"type": "str"},
                        "hostname": {"type": "str"},
                        "location": {"type": "str"},
                    },
                    "type": "dict",
                },
                "banner": {"type": "str"},
                "cell_reliability_test": {
                    "options": {
                        "enabled": {"type": "bool"},
                        "period": {"type": "int"},
                        "signal_strength_threshold": {
                            "options": {
                                "lower": {"type": "int"},
                                "upper": {"type": "int"},
                            },
                            "type": "dict",
                        },
                        "test_url": {"elements": "str", "type": "list"},
                    },
                    "type": "dict",
                },
                "cellular_logging": {
                    "options": {
                        "device": {"type": "str"},
                        "enabled": {"type": "bool"},
                        "filter": {"type": "str"},
                    },
                    "type": "dict",
                },
                "fips": {
                    "options": {
                        "enabled": {"type": "bool"},
                    },
                    "type": "dict",
                },
                "session_timeout": {
                    "options": {
                        "cli_timeout": {"type": "int"},
                        "serial_port_timeout": {"type": "int"},
                        "webui_timeout": {"type": "int"},
                    },
                    "type": "dict",
                },
                "ssh_port": {"type": "int"},
            },
            "type": "dict",
        },
        "state": {
            "choices": ["merged", "replaced", "gathered", "rendered"],
            "default": "merged",
            "type": "str",
        },
    }


# Maps each config field to its REST endpoint and the sequence of keys the
# value must be wrapped in (facts) / unwrapped from (config) to form the
# request/response body. Consumed by SystemConfig and SystemFacts.
FIELD_MAP = {
    "admin_info": ("system/admin_info", ["system_admin_info"]),
    "banner": ("system/banner", ["system_banner", "banner"]),
    "cell_reliability_test": ("system/cell_reliability_test", ["cell_reliability_test"]),
    "cellular_logging": ("system/cellular_logging", ["system_cellular_logging"]),
    "fips": ("system/fips", ["fips"]),
    "session_timeout": ("system/session_timeout", ["system_session_timeout"]),
    "ssh_port": ("system/ssh_port", ["system_ssh_port", "port"]),
}
