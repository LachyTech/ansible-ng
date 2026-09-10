# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.config.collection import CollectionConfigBase


class ServicesSyslog(CollectionConfigBase):
    """
    Manages remote syslog server configuration on Opengear devices.

    Each record is identified by the (address, port, protocol) tuple, since
    syslog servers have no user-assigned name (this mirrors the device's own
    multi_field_identifier, which is built from the same three fields).
    """

    resource_name = 'services_syslog'
    endpoint = 'services/syslog'
    item_key = 'syslogServer'
    identity_fields = ('address', 'port', 'protocol')
