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
        sha256="00f2788bcebb5f8521787662711513bc9ddf6c84e9b9a88ee96c5c2ed03f9537",
    )
    depends_on("py-setuptools", type="build")
    depends_on("c", type="build")
