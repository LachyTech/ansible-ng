# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class LocalPasswordPolicyArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the local_password_policy module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "password_expiry_interval_enabled": {"type": "bool"},
                "password_expiry_interval_days": {"type": "int", "no_log": False},
                "password_complexity_enabled": {"type": "bool"},
                "password_minimum_length": {"type": "int", "no_log": False},
                "password_must_contain_upper_case": {"type": "bool"},
                "password_must_contain_special": {"type": "bool"},
                "password_must_contain_number": {"type": "bool"},
                "password_disallow_username": {"type": "bool"},
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
