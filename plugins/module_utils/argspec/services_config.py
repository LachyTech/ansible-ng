# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ServicesConfigArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the services_config module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "options": {
                "brute_force_protection": {
                    "options": {
                        "ssh_enabled": {"type": "bool"},
                        "https_enabled": {"type": "bool"},
                        "max_retry": {"type": "int"},
                        "ban_time": {"type": "int"},
                        "find_time": {"type": "int"},
                    },
                    "type": "dict",
                },
                "https_certificate": {
                    "options": {
                        "cert": {"type": "str"},
                        "key": {"type": "str", "no_log": True},
                    },
                    "type": "dict",
                },
                "lldp": {
                    "options": {
                        "enabled": {"type": "bool"},
                        "description": {"type": "str"},
                        "platform": {"type": "str"},
                        "portid_subtype": {"type": "str", "choices": ["macaddress", "ifname"]},
                        "physifs": {"type": "list", "elements": "str"},
                    },
                    "type": "dict",
                },
                "ntp": {
                    "options": {
                        "enabled": {"type": "bool"},
                        "servers": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "value": {"type": "str"},
                                "key": {
                                    "type": "dict",
                                    "options": {
                                        "value": {"type": "str", "no_log": True},
                                        "index": {"type": "int"},
                                        "format": {"type": "str", "choices": ["ASCII", "HEX"]},
                                        "algorithm": {
                                            "type": "str",
                                            "choices": [
                                                "MD5", "SHA1", "SHA256", "SHA384", "SHA512",
                                                "SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512",
                                                "AES128", "AES256",
                                            ],
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "type": "dict",
                },
                "perifrouted": {
                    "options": {
                        "enabled": {"type": "bool"},
                    },
                    "type": "dict",
                },
                "routing": {
                    "options": {
                        "bgpd": {
                            "options": {"enabled": {"type": "bool"}},
                            "type": "dict",
                        },
                        "isisd": {
                            "options": {"enabled": {"type": "bool"}},
                            "type": "dict",
                        },
                        "ripd": {
                            "options": {"enabled": {"type": "bool"}},
                            "type": "dict",
                        },
                        "ospfd": {
                            "options": {
                                "enabled": {"type": "bool"},
                                "router_id": {"type": "str"},
                                "redistribute_connected": {"type": "bool"},
                                "redistribute_static": {"type": "bool"},
                                "redistribute_kernel": {"type": "bool"},
                                "maximum_paths": {"type": "int"},
                                "managed_by": {"type": "str"},
                                "interfaces": {
                                    "type": "list",
                                    "elements": "dict",
                                    "options": {
                                        "name": {"type": "str"},
                                        "cost": {"type": "int"},
                                        "hello_interval": {"type": "int"},
                                        "dead_interval": {"type": "int"},
                                        "priority": {"type": "int"},
                                        "area": {"type": "str"},
                                        "non_broadcast": {"type": "bool"},
                                        "passive": {"type": "bool"},
                                        "auth_method": {
                                            "type": "str",
                                            "choices": ["no_auth", "cleartext", "md5"],
                                        },
                                        "auth_keys": {
                                            "type": "list",
                                            "elements": "dict",
                                            "options": {
                                                "id": {"type": "str"},
                                                "key": {"type": "str", "no_log": True},
                                            },
                                        },
                                    },
                                },
                                "neighbors": {
                                    "type": "list",
                                    "elements": "dict",
                                    "options": {
                                        "address": {"type": "str"},
                                    },
                                },
                                "networks": {
                                    "type": "list",
                                    "elements": "dict",
                                    "options": {
                                        "address_with_mask": {"type": "str"},
                                        "area": {"type": "str"},
                                    },
                                },
                            },
                            "type": "dict",
                        },
                    },
                    "type": "dict",
                },
                "snmpd": {
                    "options": {
                        "enabled": {"type": "bool"},
                        "port": {"type": "int"},
                        "protocol": {"type": "str"},
                        "enable_legacy_versions": {"type": "bool"},
                        "rocommunity": {"type": "str"},
                        "rwcommunity": {"type": "str"},
                        "enable_secure_snmp": {"type": "bool"},
                        "security_level": {"type": "str"},
                        "security_name": {"type": "str"},
                        "engine_id": {"type": "str"},
                        "auth_protocol": {"type": "str"},
                        "auth_use_plaintext": {"type": "bool"},
                        "auth_password": {"type": "str", "no_log": True},
                        "auth_localized_key": {"type": "str", "no_log": True},
                        "priv_protocol": {"type": "str"},
                        "priv_use_plaintext": {"type": "bool"},
                        "priv_password": {"type": "str", "no_log": True},
                        "priv_localized_key": {"type": "str", "no_log": True},
                    },
                    "type": "dict",
                },
                "ssh": {
                    "options": {
                        "ssh_url_delimiter": {"type": "str"},
                        "maxstartups_start": {"type": "int"},
                        "maxstartups_rate": {"type": "int"},
                        "maxstartups_full": {"type": "int"},
                        "unauthenticated_serial_port_access": {"type": "bool"},
                        "alternate_base_port": {"type": "int"},
                    },
                    "type": "dict",
                },
                "tftp": {
                    "options": {
                        "enabled": {"type": "bool"},
                        "path": {"type": "str"},
                    },
                    "type": "dict",
                },
                "web": {
                    "options": {
                        "allow_remote_access": {"type": "bool"},
                    },
                    "type": "dict",
                },
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
# request/response body. Consumed by ServicesConfig and ServicesConfigFacts.
FIELD_MAP = {
    "brute_force_protection": ("services/brute_force_protection", ["brute_force_protection"]),
    "https_certificate": ("services/https/certificate", ["https_certificate"]),
    "lldp": ("services/lldp", ["lldp"]),
    "ntp": ("services/ntp", ["ntp"]),
    "perifrouted": ("services/perifrouted", ["perifrouted"]),
    "routing": ("services/routing", ["routing"]),
    "snmpd": ("services/snmpd", ["snmpd"]),
    "ssh": ("services/ssh", ["ssh"]),
    "tftp": ("services/tftp", ["tftp"]),
    "web": ("services/web", ["web"]),
}
