# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_time import FIELD_MAP, SystemTimeArgs
from ansible_collections.opengear.ng.plugins.module_utils.facts.singleton import SingletonFacts


class SystemTimeFacts(SingletonFacts):
    """
    Retrieves the system clock and timezone facts from Opengear devices.
    """

    resource_name = 'system_time'
    args = SystemTimeArgs
    field_map = FIELD_MAP

    @property
    def gather_exclude(self):
        """ The device clock is always advancing, so by default it is excluded
        from fact gathering and from before/after diffs. It is only returned
        when the user explicitly opts in with ``gather_time`` on a ``gathered``
        run - never during action states, so it can't leak into a diff.
        """
        params = self._module.params
        if params.get('state') == 'gathered' and params.get('gather_time'):
            return ()
        return ('time',)
