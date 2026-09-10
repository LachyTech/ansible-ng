# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.services_config import FIELD_MAP
from ansible_collections.opengear.ng.plugins.module_utils.config.singleton import SingletonConfigBase


class ServicesConfig(SingletonConfigBase):
    """
    Manages configuration of singleton services on Opengear devices (brute
    force protection, HTTPS certificate, TFTP, NTP, LLDP, SNMP daemon, SSH,
    routing daemons, web remote access, Perifrouted).
    """

    resource_name = 'services_config'
    field_map = FIELD_MAP
