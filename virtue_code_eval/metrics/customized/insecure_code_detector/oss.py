# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from __future__ import annotations

import functools
import importlib.resources

import os
import shutil
import warnings
from pathlib import Path

# We use buck internally to bundle the code into a .par file which
# can't access the rules directly. Hence the special casing here.
RULES_ROOT: Path = Path(__file__).parent / "rules"
ENABLE_REGEX_ANALYZER = True

ENABLE_WEGGLI = False
WEGGLI_COMMAND: list[str] = [
    os.environ.get("WEGGLI_PATH", "weggli"),
    "-n",
    "-C",
    "-A 0",
    "-B 0",
]

ENABLE_SEMGREP: bool = True
SEMGREP_RULE_REPO_PATH: Path = Path(__file__).parent / "rules" / "semgrep"


def _get_semgrep_core_path() -> Path | None:
    semgrep_core_name = "semgrep-core"
    try:
        with importlib.resources.path("semgrep.bin", semgrep_core_name) as path:
            if path.is_file():
                return path
    except (FileNotFoundError, ModuleNotFoundError):
        pass

    path = shutil.which(semgrep_core_name)
    if path is not None:
        return Path(path)

    warnings.warn(
        f"Failed to locate {semgrep_core_name} binary in system PATH or within the semgrep package distribution. "
        "Without this, the insecure_code_detector metric cannot function."
        "This will impact all CyberSecEval-related tasks. "
        "Resolution: Install semgrep via 'pip install semgrep' or ensure semgrep-core is accessible in your system PATH.",
        RuntimeWarning,
        stacklevel = 2
    )
    return None


@functools.lru_cache(maxsize = None)
def _make_semgrep_binary_path() -> Path:
    # create symlink to semgrep-core
    source = _get_semgrep_core_path()
    if source is None:
        return Path("")
    destination = Path(str(source).replace("semgrep-core", "osemgrep"))
    if not os.path.islink(destination):
        os.symlink(source, destination)
    return Path(destination)


SEMGREP_BINARY_PATH: Path = _make_semgrep_binary_path()
SEMGREP_COMMAND: list[str] = [
    str(SEMGREP_BINARY_PATH),
    "--experimental",
    "--optimizations",
    "all",
    "--metrics",
    "off",
    "--quiet",
    "--json",
    "--config",
]
