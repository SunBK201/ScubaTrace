from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import tempfile
from enum import Enum

import networkx as nx
from pygraphviz import AGraph


class Language(Enum):
    JAVA = "javasrc"
    C = "newc"
    CPP = "newcpp"
    PYTHON = "python"
    JAVASCRIPT = "javascript"


class Joern:
    def __init__(
        self, code_path: str, language: Language, cache_path: str | None = None
    ):
        self.code_path = code_path
        self.language = language

        self.cache_path = tempfile.mkdtemp() if cache_path is None else cache_path
        self.pdg_dir = os.path.join(self.cache_path, "pdg")
        self.cfg_dir = os.path.join(self.cache_path, "cfg")
        self.cpg_dir = os.path.join(self.cache_path, "cpg")
        self.cg_dir = os.path.join(self.cache_path, "cg")
        self.cpg_bin = os.path.join(self.cache_path, "cpg.bin")

    def close(self):
        if os.path.exists(self.cache_path):
            shutil.rmtree(self.cache_path)

    @property
    def callgraph(self) -> nx.MultiDiGraph:
        cg_path = os.path.join(self.cg_dir, "cg.dot")
        if not os.path.exists(cg_path):
            raise FileNotFoundError(f"Callgraph not found at {cg_path}")
        cg: nx.MultiDiGraph = nx.nx_agraph.read_dot(cg_path)
        return cg

    def export(self, overwrite: bool = False):
        pdg_dir = self.pdg_dir
        cfg_dir = self.cfg_dir
        cpg_dir = self.cpg_dir
        cg_dir = self.cg_dir
        cpg_bin = self.cpg_bin
        if (
            os.path.exists(pdg_dir)
            and os.path.exists(cfg_dir)
            and os.path.exists(cpg_dir)
            and not overwrite
        ):
            return
        else:
            if os.path.exists(pdg_dir):
                subprocess.run(["rm", "-rf", pdg_dir])
            if os.path.exists(cfg_dir):
                subprocess.run(["rm", "-rf", cfg_dir])
            if os.path.exists(cpg_bin):
                subprocess.run(["rm", "-rf", cpg_bin])
            if os.path.exists(cpg_dir):
                subprocess.run(["rm", "-rf", cpg_dir])

        if self.language is not None:
            lang = (
                Language.C.value
                if self.language == Language.CPP
                else self.language.value
            )
            subprocess.run(
                ["joern-parse", "--language", lang, os.path.abspath(self.code_path)],
                cwd=self.cache_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.run(
                ["joern-parse", os.path.abspath(self.code_path)],
                cwd=self.cache_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        subprocess.run(
            ["joern-export", "--repr", "cfg", "--out", os.path.abspath(cfg_dir)],
            cwd=self.cache_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["joern-export", "--repr", "pdg", "--out", os.path.abspath(pdg_dir)],
            cwd=self.cache_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["joern-export", "--repr", "all", "--out", os.path.abspath(cpg_dir)],
            cwd=self.cache_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if overwrite or not os.path.exists(cg_dir):
            if os.path.exists(cg_dir):
                subprocess.run(["rm", "-rf", cg_dir])
            self.export_cg()

    def export_with_preprocess(
        self,
        need_cdg: bool = False,
        overwrite: bool = False,
    ):
        self.export(
            overwrite=overwrite,
        )
        pdg_dir = self.pdg_dir
        pdg_old_dir = os.path.join(self.cache_path, "pdg-old")

        if overwrite or not os.path.exists(pdg_old_dir):
            if os.path.exists(pdg_old_dir):
                subprocess.run(["rm", "-rf", pdg_old_dir])
            subprocess.run(["cp", "-r", pdg_dir, pdg_old_dir])
            self.preprocess(need_cdg)

    def export_cg(self):
        if not os.path.exists(self.cg_dir):
            os.makedirs(self.cg_dir)
        cpg_path = os.path.join(self.cpg_dir, "export.dot")
        if not os.path.exists(cpg_path):
            raise FileNotFoundError(f"export.dot is not found in {cpg_path}")
        cpg: nx.MultiDiGraph = nx.nx_agraph.read_dot(cpg_path)
        cg: nx.MultiDiGraph = nx.MultiDiGraph()

        def is_method_node(node: int) -> bool:
            node_type = cpg.nodes[node]["label"]
            if node_type == "METHOD":
                if re.match(r"^<.*>.*", cpg.nodes[node]["FULL_NAME"]) or re.match(
                    r".*<.*>", cpg.nodes[node]["NAME"]
                ):
                    return False
                if cpg.nodes[node]["NAME"] == "<global>":
                    return False
                if (
                    cpg.nodes[node]["CODE"].strip().endswith(");")
                ):  # function declaration
                    return False
                return True
            return False

        def is_call_node(node: int) -> bool:
            node_type = cpg.nodes[node]["label"]
            if node_type == "CALL":
                if re.match(r"^<.*>.*", cpg.nodes[node]["METHOD_FULL_NAME"]):
                    return False
                return True
            return False

        # extracting method nodes from cpg to cg
        for node in cpg.nodes():
            if not is_method_node(node):
                continue
            cg.add_node(node, **cpg.nodes[node])
            cg.nodes[node]["NODE_TYPE"] = cg.nodes[node]["label"]
            cg.nodes[node]["label"] = cg.nodes[node]["CODE"].split("\n")[0]
            if cg.nodes[node]["CODE"] == "<empty>":
                cg.nodes[node]["label"] = cg.nodes[node]["NAME"]

        # extracting edges which type is CALL from cpg to cg
        for u, v, data in cpg.edges(data=True):
            if not is_call_node(u) or not is_method_node(v):
                continue
            if "label" not in data or data["label"] != "CALL":
                continue
            call_start_line = int(cpg.nodes[u]["LINE_NUMBER"])
            call_start_cloumn = int(cpg.nodes[u]["COLUMN_NUMBER"])

            # search caller filename: caller -> u (label is CONTAINS)
            caller_filename = None
            for caller in cpg.predecessors(u):
                # check every edge of caller -> u
                for edge in cpg[caller][u].values():
                    if "label" not in edge:
                        continue
                    if edge["label"] != "CONTAINS":
                        continue
                    caller_filename = cpg.nodes[caller]["FILENAME"]
                    break
                if caller_filename is not None:
                    break
            if caller_filename is None:
                logging.warning(f"Caller filename not found for node {u}")
                continue

            # search caller method node by call node
            for method_node in cg.nodes():
                if "NODE_TYPE" not in cg.nodes[method_node]:
                    continue
                if cg.nodes[method_node]["NODE_TYPE"] != "METHOD":
                    continue
                if cg.nodes[method_node]["IS_EXTERNAL"] == "true":
                    continue
                if cg.nodes[method_node]["FILENAME"] != caller_filename:
                    continue
                method_start_line = int(cg.nodes[method_node]["LINE_NUMBER"])
                method_end_line = int(cg.nodes[method_node]["LINE_NUMBER_END"])
                if method_start_line <= call_start_line <= method_end_line:
                    edge_key = str(call_start_line) + ":" + str(call_start_cloumn)
                    cg.add_edge(method_node, v, edge_key, **cpg.nodes[u])
                    cg.edges[method_node, v, edge_key]["label"] = cg.edges[
                        method_node, v, edge_key
                    ]["LINE_NUMBER"]
                    break

        # color red for IS_EXTERNAL node
        for method_node in cg.nodes():
            if "NODE_TYPE" not in cg.nodes[method_node]:
                continue
            if cg.nodes[method_node]["NODE_TYPE"] != "METHOD":
                continue
            if cg.nodes[method_node]["IS_EXTERNAL"] == "true":
                cg.nodes[method_node]["color"] = "red"

        # remove cycle edges
        def remove_cycles(G):
            try:
                cycle = nx.find_cycle(G, orientation="original")
                edge_to_remove = cycle[0]
                G.remove_edge(edge_to_remove[0], edge_to_remove[1])
                remove_cycles(G)
            except nx.exception.NetworkXNoCycle:
                ...
            return G

        cg = remove_cycles(cg)

        ag: AGraph = nx.nx_agraph.to_agraph(cg)
        ag.graph_attr["bgcolor"] = "ivory"
        ag.graph_attr["splines"] = "true"
        ag.node_attr["fontname"] = "SF Pro Rounded, system-ui"
        ag.node_attr["shape"] = "box"
        ag.node_attr["style"] = "rounded"
        ag.node_attr["margin"] = "0.5,0.1"
        ag.edge_attr["fontname"] = "SF Pro Rounded, system-ui"
        ag.edge_attr["arrowhead"] = "vee"
        # writing cg to dot file
        cg_path = os.path.join(self.cg_dir, "cg.dot")
        ag.write(cg_path)

    def preprocess(self, need_cdg: bool):
        cpg = nx.nx_agraph.read_dot(os.path.join(self.cpg_dir, "export.dot"))
        for pdg_file in os.listdir(self.pdg_dir):
            file_id = pdg_file.split("-")[0]
            try:
                pdg: nx.MultiDiGraph = nx.nx_agraph.read_dot(
                    os.path.join(self.pdg_dir, pdg_file)
                )
                cfg: nx.MultiDiGraph = nx.nx_agraph.read_dot(
                    os.path.join(self.cfg_dir, f"{file_id}-cfg.dot")
                )
            except Exception as e:
                logging.error(f"Error in reading {pdg_file} or {file_id}-cfg.dot")
                os.remove(os.path.join(self.pdg_dir, pdg_file))
                os.remove(os.path.join(self.cfg_dir, f"{file_id}-cfg.dot"))
                continue

            # delete some ddg_edges without any information
            ddg_null_edges = []
            for u, v, k, d in pdg.edges(data=True, keys=True):
                if need_cdg:
                    null_edges_label = ["DDG: ", "DDG: this"]
                else:
                    null_edges_label = ["DDG: ", "CDG: ", "DDG: this"]
                if d["label"] in null_edges_label:
                    ddg_null_edges.append((u, v, k, d))
            pdg.remove_edges_from(ddg_null_edges)

            pdg: nx.MultiDiGraph = nx.compose(pdg, cfg)
            for u, v, k, d in pdg.edges(data=True, keys=True):
                if "label" not in d:
                    pdg.edges[u, v, k]["label"] = "CFG"

            method_node = None
            param_nodes = []
            for node in pdg.nodes:
                for key, value in cpg.nodes[node].items():
                    pdg.nodes[node][key] = value
                pdg.nodes[node]["NODE_TYPE"] = pdg.nodes[node]["label"]
                node_type = pdg.nodes[node]["NODE_TYPE"]
                if node_type == "METHOD":
                    method_node = node
                if node_type == "METHOD_PARAMETER_IN":
                    param_nodes.append(node)
                if "CODE" not in pdg.nodes[node]:
                    pdg.nodes[node]["CODE"] = ""
                node_code = (
                    pdg.nodes[node]["CODE"]
                    .replace("\n", "\\n")
                    .replace('"', r"__quote__")
                    .replace("\\", r"__Backslash__")
                )
                pdg.nodes[node]["CODE"] = (
                    pdg.nodes[node]["CODE"]
                    .replace("\n", "\\n")
                    .replace('"', r"__quote__")
                    .replace("\\", r"__Backslash__")
                )
                # pdg.nodes[node]['CODE'] = ''
                node_line = (
                    pdg.nodes[node]["LINE_NUMBER"]
                    if "LINE_NUMBER" in pdg.nodes[node]
                    else 0
                )
                node_column = (
                    pdg.nodes[node]["COLUMN_NUMBER"]
                    if "COLUMN_NUMBER" in pdg.nodes[node]
                    else 0
                )
                pdg.nodes[node]["label"] = (
                    f"[{node}][{node_line}:{node_column}][{node_type}]: {node_code}"
                )
                if pdg.nodes[node]["NODE_TYPE"] == "METHOD_RETURN":
                    pdg.remove_edges_from(list(pdg.in_edges(node)))
            for param_node in param_nodes:
                pdg.add_edge(method_node, param_node, label="DDG")

            nx.nx_agraph.write_dot(pdg, os.path.join(self.pdg_dir, pdg_file))
