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
        sha256="4b6b6f306513cf0314451d959afd64f87c58f2d52571cb43c5da344bd5bc1638",
    )
    depends_on("py-setuptools", type="build")
    depends_on("c", type="build")
