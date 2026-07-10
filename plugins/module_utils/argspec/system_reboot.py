# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class SystemRebootArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the system_reboot module.

    Reboot is an action, not a stateful resource, so it takes no ``config`` or
    ``state`` - invoking the module triggers a reboot of the appliance.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {}
