# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class SystemFactoryResetArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the system_factory_reset module.

    Factory reset is a destructive action, not a stateful resource, so it takes
    no ``config`` or ``state`` - invoking the module erases the device
    configuration and restores factory defaults.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {}
