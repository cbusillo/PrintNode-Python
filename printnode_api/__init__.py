"""Preferred import namespace for the community-maintained PrintNode client.

The historical import package is ``printnodeapi``. It remains supported for
compatibility, while new code may import from ``printnode_api`` to match the
maintained distribution name more closely.
"""

from printnodeapi import *  # noqa: F401,F403
