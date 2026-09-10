# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ServicesSyslogArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the services_syslog module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "id": {"type": "str"},
                "multi_field_identifier": {"type": "str"},
                "address": {"type": "str", "required": True},
                "port": {"type": "int"},
                "protocol": {"type": "str", "choices": ["TCP", "UDP"]},
                "description": {"type": "str"},
                "port_logging_enabled": {"type": "bool"},
                "min_severity": {
                    "type": "str",
                    "choices": [
                        "emergency", "alert", "critical", "error",
                        "warning", "notice", "info", "debug",
                    ],
                },
            },
        },
        "state": {
            "type": "str",
            "default": "merged",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered"],
        },
    }
