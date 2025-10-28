# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import pathlib
from spack_repo.builtin.build_systems.python import PythonPackage

from spack.package import *

class PyPosixmq(PythonPackage):
    url = f"file:///{pathlib.PurePath(__file__).parent}/pymq.tar.gz"
    version(
        "1.0",
        sha256="df42d69c8dce2939981cff2d2f76e7c80a30fe307e8d19ef12357d27f564df3a",
    )
    depends_on("py-setuptools", type="build")
    depends_on("c", type="build")
