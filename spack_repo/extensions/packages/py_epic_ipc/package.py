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
        sha256="8e53f4cf4192c676e456f6dd57a5fbe6a661984cb99869b2b0dc29c33193e352",
    )
    depends_on("py-setuptools", type="build")
    depends_on("c", type="build")
