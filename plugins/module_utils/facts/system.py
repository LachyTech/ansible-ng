# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.system import FIELD_MAP, SystemArgs
from ansible_collections.opengear.ng.plugins.module_utils.facts.singleton import SingletonFacts


class SystemFacts(SingletonFacts):
    """
    Retrieves and parses scalar system settings facts from Opengear devices.
    """

    resource_name = 'system_config'
    args = SystemArgs
    field_map = FIELD_MAP
    optional_fields = ('cell_reliability_test', 'cellular_logging')
