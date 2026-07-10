# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.system import FIELD_MAP
from ansible_collections.opengear.ng.plugins.module_utils.config.singleton import SingletonConfigBase


class System(SingletonConfigBase):
    """
    Manages configuration of general system settings on Opengear devices
    (banner, hostname, SSH port, session timeouts and admin info).
    """

    resource_name = 'system_config'
    field_map = FIELD_MAP
