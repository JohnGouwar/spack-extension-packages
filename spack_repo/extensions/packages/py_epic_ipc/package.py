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
        sha256="bfd18bfee221ce5ba115b1d78f193863b5f02771c302549048e5bbebfa187fda",
    )
    depends_on("py-setuptools", type="build")
    depends_on("c", type="build")
