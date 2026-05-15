from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from . import language as lang
from .language import Language


class JoernLanguage(Enum):
    JAVA = "javasrc"
    C = "newcpp"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    GO = "golang"
    PHP = "php"
    CSHARP = "csharp"


@dataclass
class JoernConfig:
    """Configuration for Joern integration.

    :param enable: Whether to enable Joern integration.
    :param cpg_path: Path to an existing ``cpg.bin`` file. If specified,
        joern-parse is skipped when the file exists. If the path does not
        exist, joern-parse is called to generate ``cpg.bin``.
    :param cpg_output_dir: Output directory for joern-parse. This is effective
        only when ``cpg_path`` is not specified.
    :param overwrite: Whether to overwrite existing CPG output when the output
        directory already exists.
    :param joern_parse_path: Path to the joern-parse executable. If not specified,
        it is assumed to be in the system PATH.
    :param Language: The programming language of the source code.
    """

    enable: bool = True
    cpg_path: str | None = None
    cpg_output_dir: str | None = None
    overwrite: bool = False
    joern_parse_path: str | None = None
    Language: Language | None = None


def parse(source_dir: str, config: JoernConfig) -> Path:
    """Run joern-parse on the given source directory.

    :param source_dir: Path to the source code directory.
    :param config: JoernConfig object containing configuration for Joern integration.
    :return: Path to the generated ``cpg.bin`` file.
    """
    if not config.enable:
        raise ValueError("Joern integration is disabled in the configuration")

    if config.cpg_path is not None:
        cpg_path = Path(config.cpg_path)
        if cpg_path.exists():
            return cpg_path
        else:
            print(f"CPG file {cpg_path} does not exist. Running joern-parse...")

    output_dir = config.cpg_output_dir
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="joern_output_")
    elif os.path.exists(output_dir):
        if config.overwrite:
            shutil.rmtree(output_dir)
        else:
            raise FileExistsError(f"Output directory {output_dir} already exists")

    os.makedirs(output_dir, exist_ok=True)

    joern_parse_executable = config.joern_parse_path or "joern-parse"
    if shutil.which(joern_parse_executable) is None:
        raise FileNotFoundError(
            f"Joern-parse executable '{joern_parse_executable}' not found in PATH. "
            "Please specify the correct path in the configuration."
        )

    if config.Language is not None:
        joern_language = _language_to_joern_language(config.Language)
        subprocess.run(
            [
                joern_parse_executable,
                "--language",
                joern_language.value,
                os.path.abspath(source_dir),
            ],
            cwd=output_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(
            [joern_parse_executable, os.path.abspath(source_dir)],
            cwd=output_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return Path(output_dir) / "cpg.bin"


def _language_to_joern_language(language: Language) -> JoernLanguage:
    if language == lang.C:
        return JoernLanguage.C
    elif language == lang.JAVA:
        return JoernLanguage.JAVA
    elif language == lang.PYTHON:
        return JoernLanguage.PYTHON
    elif language == lang.JAVASCRIPT:
        return JoernLanguage.JAVASCRIPT
    elif language == lang.GO:
        return JoernLanguage.GO
    elif language == lang.PHP:
        return JoernLanguage.PHP
    elif language == lang.CSHARP:
        return JoernLanguage.CSHARP
    else:
        raise ValueError(f"Unsupported language with extensions: {language.extensions}")
