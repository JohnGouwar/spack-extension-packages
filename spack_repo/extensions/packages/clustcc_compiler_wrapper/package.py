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
            "3.1415",
            sha256="896e96555f4721a3916471dc520dad19041f37c09624164bb8be2e0a27d34d31",
            expand=False,
        )
        # Dependency actually needed for tracing
        depends_on("clustcc-client", when="@3.1415", type=("build", "link", "run"))


