# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ServicesSnmpAlertManagersArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the services_snmp_alert_managers module.
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
                "name": {"type": "str", "required": True},
                "protocol": {"type": "str", "choices": ["UDP", "TCP", "UDP6", "TCP6"]},
                "address": {"type": "str"},
                "port": {"type": "int"},
                "msg_type": {"type": "str", "choices": ["TRAP", "INFORM"]},
                "version": {"type": "str", "choices": ["v1", "v2c", "v3"]},
                "community": {"type": "str", "no_log": True},
                "auth_protocol": {"type": "str"},
                "auth_password": {"type": "str", "no_log": True},
                "username": {"type": "str"},
                "engine_id": {"type": "str"},
                "privacy_protocol": {"type": "str"},
                "privacy_password": {"type": "str", "no_log": True},
                "security_level": {"type": "str", "choices": ["noAuthNoPriv", "authNoPriv", "authPriv"]},
            },
        },
        "state": {
            "type": "str",
            "default": "merged",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered"],
        },
    }
