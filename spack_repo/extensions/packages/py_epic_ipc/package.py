# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import pathlib
from spack_repo.builtin.build_systems.python import PythonPackage

from spack.package import *

class PyEpicIpc(PythonPackage):
    url = f"file:///{pathlib.PurePath(__file__).parent}/epic_ipc.tar.gz"
    version(
        "1.0",
        sha256="f87635e379ea8ef84857125ed231346ff4031f8858996a3dc69151f66323fd79",
    )
    depends_on("py-setuptools", type="build")
    depends_on("c", type="build")
