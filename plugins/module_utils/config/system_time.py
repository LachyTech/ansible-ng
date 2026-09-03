# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_time import FIELD_MAP
from ansible_collections.opengear.ng.plugins.module_utils.config.singleton import SingletonConfigBase


class SystemTime(SingletonConfigBase):
    """
    Manages the system clock and timezone on Opengear devices.

    C(timezone) is idempotent; C(time) is not - setting it always reports a
    change because the device clock advances between fact gathering and
    comparison. C(time) is only ever pushed when explicitly provided.
    """

    resource_name = 'system_time'
    field_map = FIELD_MAP
