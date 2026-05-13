from __future__ import annotations

from .model import CpgNode
from .schema import build_node_classes

NODE_CLASS_BY_LABEL = build_node_classes(CpgNode)
globals().update({cls.__name__: cls for cls in NODE_CLASS_BY_LABEL.values()})

__all__ = ["NODE_CLASS_BY_LABEL", *[cls.__name__ for cls in NODE_CLASS_BY_LABEL.values()]]

