# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.services_config import FIELD_MAP, ServicesConfigArgs
from ansible_collections.opengear.ng.plugins.module_utils.facts.singleton import SingletonFacts


class ServicesConfigFacts(SingletonFacts):
    """
    Retrieves and parses singleton services facts from Opengear devices.
    """

    resource_name = 'services_config'
    args = ServicesConfigArgs
    field_map = FIELD_MAP
