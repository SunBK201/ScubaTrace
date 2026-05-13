from __future__ import annotations

import json
import struct
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import zstandard as zstd

from .model import CPG, CpgEdge, CpgNode, NodeId
from .objects import NODE_CLASS_BY_LABEL
from .schema import CPG_EDGE_LABELS, CPG_NODE_SCHEMA

MAGIC = b"FLT GRPH"
HEADER_SIZE = 16


class FlatGraphFormatError(ValueError):
    pass


class FlatGraphReader:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data = self.path.read_bytes()
        self.manifest = self._read_manifest()
        self._validate_manifest_schema()
        self._string_pool: list[str] | None = None

    def read(self) -> CPG:
        node_labels = [item["nodeLabel"] for item in self.manifest["nodes"]]
        nodes = self._create_nodes()
        self._read_properties(nodes)
        edges = list(self._read_edges(node_labels))
        return CPG(nodes, edges, manifest=self.manifest)

    def _read_manifest(self) -> dict[str, Any]:
        if len(self._data) < HEADER_SIZE:
            raise FlatGraphFormatError("File is too small to be a FlatGraph file")
        if self._data[: len(MAGIC)] != MAGIC:
            raise FlatGraphFormatError("Missing FlatGraph magic header")
        manifest_offset = struct.unpack_from("<Q", self._data, len(MAGIC))[0]
        if manifest_offset >= len(self._data):
            raise FlatGraphFormatError("Manifest offset points outside the file")
        return json.loads(self._data[manifest_offset:].decode("utf-8"))

    def _decompress(self, outline: Mapping[str, Any] | None) -> bytes | None:
        if outline is None:
            return None
        start = int(outline["startOffset"])
        end = start + int(outline["compressedLength"])
        expected = int(outline["decompressedLength"])
        return zstd.ZstdDecompressor().decompress(
            self._data[start:end], max_output_size=expected
        )

    def _array(self, outline: Mapping[str, Any] | None) -> list[Any] | None:
        if outline is None:
            return None
        raw = self._decompress(outline)
        if raw is None:
            return None
        typ = outline["type"]
        if typ == "bool":
            return [value != 0 for value in raw]
        if typ == "byte":
            return list(raw)
        if typ == "short":
            return list(struct.unpack(f"<{len(raw) // 2}h", raw))
        if typ == "int":
            return list(struct.unpack(f"<{len(raw) // 4}i", raw))
        if typ == "long":
            return list(struct.unpack(f"<{len(raw) // 8}q", raw))
        if typ == "float":
            return list(struct.unpack(f"<{len(raw) // 4}f", raw))
        if typ == "double":
            return list(struct.unpack(f"<{len(raw) // 8}d", raw))
        if typ == "string":
            pool = self._read_string_pool()
            indexes = struct.unpack(f"<{len(raw) // 4}i", raw)
            return [pool[index] if index >= 0 else None for index in indexes]
        if typ == "ref":
            refs = struct.unpack(f"<{len(raw) // 8}Q", raw)
            labels = [item["nodeLabel"] for item in self.manifest["nodes"]]
            result: list[NodeId | None] = []
            for ref in refs:
                kind = ref >> 32
                seq = ref & 0xFFFFFFFF
                if kind >= len(labels):
                    result.append(None)
                else:
                    result.append((labels[kind], seq))
            return result
        raise FlatGraphFormatError(f"Unsupported FlatGraph storage type: {typ}")

    def _read_string_pool(self) -> list[str]:
        if self._string_pool is not None:
            return self._string_pool
        lengths_raw = self._decompress(self.manifest["stringPoolLength"]) or b""
        bytes_raw = self._decompress(self.manifest["stringPoolBytes"]) or b""
        lengths = struct.unpack(f"<{len(lengths_raw) // 4}i", lengths_raw)
        offset = 0
        strings: list[str] = []
        for length in lengths:
            chunk = bytes_raw[offset : offset + length]
            strings.append(chunk.decode("utf-8"))
            offset += length
        self._string_pool = strings
        return strings

    def _validate_manifest_schema(self) -> None:
        for item in self.manifest.get("nodes", ()):
            label = item["nodeLabel"]
            if label not in CPG_NODE_SCHEMA:
                raise FlatGraphFormatError(f"Unknown CPG node label: {label}")
        for item in self.manifest.get("properties", ()):
            label = item["nodeLabel"]
            prop = item["propertyLabel"]
            if prop not in CPG_NODE_SCHEMA.get(label, frozenset()):
                raise FlatGraphFormatError(
                    f"Property {prop} is not valid for CPG node label {label}"
                )
        for item in self.manifest.get("edges", ()):
            label = item["edgeLabel"]
            if label not in CPG_EDGE_LABELS:
                raise FlatGraphFormatError(f"Unknown CPG edge label: {label}")

    def _create_nodes(self) -> dict[NodeId, CpgNode]:
        nodes: dict[NodeId, CpgNode] = {}
        for item in self.manifest["nodes"]:
            label = item["nodeLabel"]
            node_cls = NODE_CLASS_BY_LABEL[label]
            deleted = set(self._array(item.get("deletions")) or [])
            for seq in range(int(item["nnodes"])):
                if seq not in deleted:
                    nodes[(label, seq)] = node_cls(
                        id=(label, seq), label=label, seq=seq
                    )
        return nodes

    def _read_properties(self, nodes: dict[NodeId, CpgNode]) -> None:
        for item in self.manifest["properties"]:
            label = item["nodeLabel"]
            prop_name = item["propertyLabel"]
            offsets = _delta_decode(self._array(item["qty"]) or [])
            values = self._array(item["property"]) or []
            for seq in range(max(0, len(offsets) - 1)):
                node = nodes.get((label, seq))
                if node is None:
                    continue
                start, end = offsets[seq], offsets[seq + 1]
                if start == end:
                    continue
                prop_values = values[start:end]
                node.properties[prop_name] = (
                    prop_values[0] if len(prop_values) == 1 else prop_values
                )
        for node in nodes.values():
            node.validate_schema()

    def _read_edges(self, node_labels: Sequence[str]) -> Iterable[CpgEdge]:
        seen_half_edges = set()
        for item in self.manifest["edges"]:
            # FlatGraph encodes Edge.Direction.Incoming as ordinal 0 and
            # Edge.Direction.Outgoing as ordinal 1.
            if int(item["inout"]) != 1:
                continue
            src_label = item["nodeLabel"]
            edge_label = item["edgeLabel"]
            offsets = _delta_decode(self._array(item["qty"]) or [])
            neighbors = self._array(item["neighbors"]) or []
            properties = (
                self._array(item.get("property")) if item.get("property") else None
            )
            for seq in range(max(0, len(offsets) - 1)):
                start, end = offsets[seq], offsets[seq + 1]
                for index, dst in enumerate(neighbors[start:end], start):
                    if dst is None:
                        continue
                    src = (src_label, seq)
                    prop = properties[index] if properties is not None else None
                    key = (src, dst, edge_label, index)
                    if key in seen_half_edges:
                        continue
                    seen_half_edges.add(key)
                    yield CpgEdge(src=src, dst=dst, label=edge_label, property=prop)


def _delta_decode(values: list[int]) -> list[int]:
    total = 0
    decoded: list[int] = []
    for value in values:
        decoded.append(total)
        total += value
    return decoded


def load(path: str | Path) -> CPG:
    return FlatGraphReader(path).read()
