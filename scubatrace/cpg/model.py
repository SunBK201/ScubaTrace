from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any, ClassVar

NodeId = tuple[str, int]


@dataclass(frozen=True)
class CpgEdge:
    src: NodeId
    dst: NodeId
    label: str
    property: Any = None


@dataclass(frozen=True)
class SourceLocation:
    filename: str | None
    line_number: int | None
    column_number: int | None
    line_number_end: int | None = None
    column_number_end: int | None = None
    offset: int | None = None
    offset_end: int | None = None


@dataclass(frozen=True)
class MethodCall:
    caller: CpgNode | None
    callee: CpgNode | None
    callsite: CpgNode

    @property
    def resolved(self) -> bool:
        return self.caller is not None and self.callee is not None

    @property
    def callsite_location(self) -> SourceLocation:
        return self.callsite.location

    @property
    def is_function_call(self) -> bool:
        target = self.callee
        if target is None:
            return _looks_like_function_callsite(self.callsite)
        return _looks_like_function_method(target)


@dataclass
class CpgNode:
    id: NodeId
    label: str
    seq: int
    properties: dict[str, Any] = field(default_factory=dict)
    _cpg: CPG | None = field(default=None, init=False, repr=False, compare=False)
    schema_label: ClassVar[str] = ""
    schema_properties: ClassVar[frozenset[str]] = frozenset()

    def get(self, key: str, default: Any = None) -> Any:
        return self.properties.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.properties[key]

    def __getattr__(self, name: str) -> Any:
        prop_name = name.upper()
        if prop_name in self.schema_properties:
            return self.properties.get(prop_name)
        raise AttributeError(f"{type(self).__name__!s} has no CPG property {name!r}")

    def validate_schema(self) -> None:
        unknown = set(self.properties) - set(self.schema_properties)
        if unknown:
            formatted = ", ".join(sorted(unknown))
            raise ValueError(
                f"{self.label} contains properties outside CPG schema: {formatted}"
            )

    def _graph(self) -> CPG:
        if self._cpg is None:
            raise RuntimeError("Node is not attached to a CPG instance")
        return self._cpg

    @property
    def location(self) -> SourceLocation:
        filename = self.properties.get("FILENAME")
        if not isinstance(filename, str):
            enclosing = (
                self._cpg.enclosing_method(self) if self._cpg is not None else None
            )
            filename = enclosing.filename if enclosing is not None else None
        return SourceLocation(
            filename=filename,
            line_number=self.properties.get("LINE_NUMBER"),
            column_number=self.properties.get("COLUMN_NUMBER"),
            line_number_end=self.properties.get("LINE_NUMBER_END"),
            column_number_end=self.properties.get("COLUMN_NUMBER_END"),
            offset=self.properties.get("OFFSET"),
            offset_end=self.properties.get("OFFSET_END"),
        )

    @property
    def callers(self) -> list[MethodCall]:
        if self.label != "METHOD":
            raise AttributeError("callers is only defined for METHOD nodes")
        if not _looks_like_function_method(self):
            return []
        graph = self._graph()
        result: list[MethodCall] = []
        for callsite in graph.predecessors(self.id, "CALL"):
            if callsite.label != "CALL":
                continue
            relation = MethodCall(
                caller=graph.enclosing_method(callsite),
                callee=self,
                callsite=callsite,
            )
            if relation.is_function_call:
                result.append(relation)
        return result

    @property
    def callees(self) -> list[MethodCall]:
        if self.label != "METHOD":
            raise AttributeError("callees is only defined for METHOD nodes")
        graph = self._graph()
        result: list[MethodCall] = []
        for callsite in graph.successors(self.id, "CONTAINS"):
            if callsite.label != "CALL":
                continue
            callees = graph.call_targets(callsite)
            if not callees:
                relation = MethodCall(caller=self, callee=None, callsite=callsite)
                if relation.is_function_call:
                    result.append(relation)
                continue
            for callee in callees:
                relation = MethodCall(caller=self, callee=callee, callsite=callsite)
                if relation.is_function_call:
                    result.append(relation)
        return result


class CPG:
    def __init__(
        self,
        nodes: Mapping[NodeId, CpgNode],
        edges: Iterable[CpgEdge],
        manifest: Mapping[str, Any] | None = None,
    ) -> None:
        self.nodes: dict[NodeId, CpgNode] = dict(nodes)
        self.edges: list[CpgEdge] = list(edges)
        self.manifest = dict(manifest or {})
        self._nodes_by_label: dict[str, list[CpgNode]] = {}
        self._out_edges: dict[NodeId, list[CpgEdge]] = {}
        self._in_edges: dict[NodeId, list[CpgEdge]] = {}
        self._methods_by_full_name: dict[str, list[CpgNode]] = {}
        for node in self.nodes.values():
            node._cpg = self
            self._nodes_by_label.setdefault(node.label, []).append(node)
            if node.label == "METHOD":
                full_name = node.properties.get("FULL_NAME")
                if isinstance(full_name, str):
                    self._methods_by_full_name.setdefault(full_name, []).append(node)
        for edge in self.edges:
            self._out_edges.setdefault(edge.src, []).append(edge)
            self._in_edges.setdefault(edge.dst, []).append(edge)

    @classmethod
    def load(cls, path: str) -> CPG:
        from .reader import load

        return load(path)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def node(self, node_id: NodeId) -> CpgNode:
        return self.nodes[node_id]

    def nodes_by_label(self, label: str) -> list[CpgNode]:
        return list(self._nodes_by_label.get(label, ()))

    def out_edges(self, node_id: NodeId, label: str | None = None) -> Iterator[CpgEdge]:
        for edge in self._out_edges.get(node_id, ()):
            if label is None or edge.label == label:
                yield edge

    def in_edges(self, node_id: NodeId, label: str | None = None) -> Iterator[CpgEdge]:
        for edge in self._in_edges.get(node_id, ()):
            if label is None or edge.label == label:
                yield edge

    def successors(
        self, node_id: NodeId, label: str | None = None
    ) -> Iterator[CpgNode]:
        for edge in self.out_edges(node_id, label):
            yield self.nodes[edge.dst]

    def predecessors(
        self, node_id: NodeId, label: str | None = None
    ) -> Iterator[CpgNode]:
        for edge in self.in_edges(node_id, label):
            yield self.nodes[edge.src]

    def enclosing_method(self, node: CpgNode) -> CpgNode | None:
        for parent in self.predecessors(node.id, "CONTAINS"):
            if parent.label == "METHOD":
                return parent
        return None

    def call_targets(self, callsite: CpgNode) -> list[CpgNode]:
        targets = [
            node
            for node in self.successors(callsite.id, "CALL")
            if node.label == "METHOD"
        ]
        if targets:
            return targets
        method_full_name = callsite.properties.get("METHOD_FULL_NAME")
        if isinstance(method_full_name, str):
            return list(self._methods_by_full_name.get(method_full_name, ()))
        return []

    def find_methods(
        self,
        name: str,
        *,
        full_name: bool = False,
        regex: bool = False,
        case_sensitive: bool = True,
    ) -> list[CpgNode]:
        prop = "FULL_NAME" if full_name else "NAME"
        methods = self.nodes_by_label("METHOD")
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(name, flags)
            return [
                method
                for method in methods
                if isinstance(method.properties.get(prop), str)
                and pattern.search(method.properties[prop])
            ]
        if case_sensitive:
            return [method for method in methods if method.properties.get(prop) == name]
        needle = name.casefold()
        return [
            method
            for method in methods
            if isinstance(method.properties.get(prop), str)
            and method.properties[prop].casefold() == needle
        ]

    def find_method(
        self,
        name: str,
        *,
        full_name: bool = False,
        regex: bool = False,
        case_sensitive: bool = True,
    ) -> CpgNode | None:
        matches = self.find_methods(
            name,
            full_name=full_name,
            regex=regex,
            case_sensitive=case_sensitive,
        )
        return matches[0] if matches else None

    def methods_at(
        self,
        filename: str,
        line_number: int,
        column_number: int | None = None,
    ) -> list[CpgNode]:
        matches = [
            method
            for method in self.nodes_by_label("METHOD")
            if _filename_matches(method.properties.get("FILENAME"), filename)
            and _contains_location(method, line_number, column_number)
        ]
        return sorted(matches, key=_method_span_key)

    def method_at(
        self,
        filename: str,
        line_number: int,
        column_number: int | None = None,
    ) -> CpgNode | None:
        matches = self.methods_at(filename, line_number, column_number)
        return matches[0] if matches else None

    def __getattr__(self, name: str) -> list[CpgNode]:
        from .schema import CPG_NODE_SCHEMA, label_to_step_name

        for label in CPG_NODE_SCHEMA:
            if label_to_step_name(label) == name:
                return self.nodes_by_label(label)
        raise AttributeError(f"CPG has no node step {name!r}")

    def to_networkx(self):
        import networkx as nx

        graph = nx.MultiDiGraph()
        for node_id, node in self.nodes.items():
            graph.add_node(node_id, label=node.label, **node.properties)
        for edge in self.edges:
            attrs = {"label": edge.label}
            if edge.property is not None:
                attrs["property"] = edge.property
            graph.add_edge(edge.src, edge.dst, **attrs)
        return graph


def _filename_matches(method_filename: Any, filename: str) -> bool:
    if not isinstance(method_filename, str):
        return False
    return method_filename == filename or method_filename.endswith(f"/{filename}")


def _contains_location(
    method: CpgNode, line_number: int, column_number: int | None
) -> bool:
    start = method.properties.get("LINE_NUMBER")
    end = method.properties.get("LINE_NUMBER_END")
    if not isinstance(start, int):
        return False
    if not isinstance(end, int):
        end = start
    if line_number < start or line_number > end:
        return False
    if column_number is None:
        return True

    start_col = method.properties.get("COLUMN_NUMBER")
    end_col = method.properties.get("COLUMN_NUMBER_END")
    if (
        line_number == start
        and isinstance(start_col, int)
        and column_number < start_col
    ):
        return False
    if line_number == end and isinstance(end_col, int) and column_number > end_col:
        return False
    return True


def _method_span_key(method: CpgNode) -> tuple[int, int, str]:
    start = method.properties.get("LINE_NUMBER")
    end = method.properties.get("LINE_NUMBER_END")
    if not isinstance(start, int):
        start = 0
    if not isinstance(end, int):
        end = start
    return (end - start, start, method.properties.get("FULL_NAME") or "")


def _looks_like_function_method(method: CpgNode) -> bool:
    full_name = method.properties.get("FULL_NAME") or ""
    name = method.properties.get("NAME") or ""
    if not isinstance(full_name, str) or not isinstance(name, str):
        return False
    if full_name.startswith("<operator>.") or name.startswith("<operator>."):
        return False
    if full_name.startswith("<operators>.") or name.startswith("<operators>."):
        return False
    if ":ANY(" in full_name:
        return False
    return True


def _looks_like_function_callsite(callsite: CpgNode) -> bool:
    method_full_name = callsite.properties.get("METHOD_FULL_NAME") or ""
    name = callsite.properties.get("NAME") or ""
    if not isinstance(method_full_name, str) or not isinstance(name, str):
        return False
    if method_full_name.startswith("<operator>.") or name.startswith("<operator>."):
        return False
    if method_full_name.startswith("<operators>.") or name.startswith("<operators>."):
        return False
    if ":ANY(" in method_full_name:
        return False
    return True
