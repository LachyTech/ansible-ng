# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.facts.collection import CollectionFacts


class ServicesSnmpAlertManagersFacts(CollectionFacts):
    """
    Retrieves SNMP Alert Manager facts from Opengear devices.
    """

    resource_name = 'services_snmp_alert_managers'
    endpoint = 'services/snmp_alert_managers'
    list_key = 'snmp_alert_managers'
