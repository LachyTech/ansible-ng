# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class AuthArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the auth module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "options": {
                "mode": {
                    "type": "str",
                    "choices": ["local", "radius", "tacacs", "ldap"],
                },
                "policy": {
                    "type": "str",
                    "choices": ["remotedownlocal", "remotelocal"],
                },
                "timeout": {"type": "int"},
                "radiusMethod": {"type": "str", "choices": ["pap", "mschapv2"]},
                "radiusAuthenticationServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "radiusAccountingServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "radiusAccountingEnabled": {"type": "bool"},
                "radiusRequireMessageAuthenticator": {"type": "bool"},
                "radiusPassword": {"type": "str", "no_log": True},
                "tacacsMethod": {"type": "str", "choices": ["pap", "chap", "login"]},
                "tacacsService": {"type": "str"},
                "tacacsAuthenticationServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "tacacsAccountingEnabled": {"type": "bool"},
                "tacacsPassword": {"type": "str", "no_log": True},
                "ldapBaseDN": {"type": "str"},
                "ldapBindDN": {"type": "str"},
                "ldapBindPassword": {"type": "str", "no_log": True},
                "ldapAuthenticationServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "ldapUsernameAttribute": {"type": "str"},
                "ldapGroupMembershipAttribute": {"type": "str"},
                "ldapIgnoreReferrals": {"type": "bool"},
                "ldapSslMode": {
                    "type": "str",
                    "choices": ["ldap_only", "ldaps_preferred", "ldaps_only"],
                },
                "ldapSslIgnoreCertErrors": {"type": "bool"},
                "ldapSslCaCert": {"type": "str"},
            },
            "type": "dict",
        },
        "state": {
            "choices": ["merged", "replaced", "overridden", "gathered", "rendered"],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301
