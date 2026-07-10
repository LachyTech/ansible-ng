# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class SystemTimeArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the system_time module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "options": {
                "time": {"type": "str"},
                "timezone": {"type": "str"},
            },
            "type": "dict",
        },
        "gather_time": {"type": "bool", "default": False},
        "state": {
            "choices": ["merged", "replaced", "gathered", "rendered"],
            "default": "merged",
            "type": "str",
        },
    }


# Maps each config field to its REST endpoint and body path.
# Consumed by SystemTime and SystemTimeFacts.
FIELD_MAP = {
    "time": ("system/time", ["time", "time"]),
    "timezone": ("system/timezone", ["system_timezone", "timezone"]),
}
