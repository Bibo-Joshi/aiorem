# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <aiorem@mahlerhome.de>
#
# SPDX-License-Identifier: MIT

__all__ = ["AbstractResourceManager", "AbstractResourceManagerCollection", "__version__"]

from .__about__ import __version__
from ._resourcemanager import AbstractResourceManager
from ._resourcemanagercollection import AbstractResourceManagerCollection
