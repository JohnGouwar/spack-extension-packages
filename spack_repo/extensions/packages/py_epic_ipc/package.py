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
        sha256="c84ffd47934f2067f91adc739b7d45404b4c0d5cba1794a58974e61aff87be93",
    )
    depends_on("py-setuptools", type="build")
    depends_on("c", type="build")
