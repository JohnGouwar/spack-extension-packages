# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import pathlib
import sys
from spack_repo.builtin.packages.compiler_wrapper.package import CompilerWrapper

from spack.package import *


class ClustccCompilerWrapper(CompilerWrapper):
    """Provides a compiler wrapper for use with spack distcc"""

    url = f"file:///{pathlib.PurePath(__file__).parent}/cc.sh"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    if sys.platform != "win32":
        version(
            "3.0",
            sha256="04584ecc96b021a36deb2a776a13e553ce31ae86b8d686530673ce5ecfa21cfd",
            expand=False,
        )
        # Dependency actually needed for tracing
        depends_on("spack-clustcc-client", type=("build", "link", "run"))


