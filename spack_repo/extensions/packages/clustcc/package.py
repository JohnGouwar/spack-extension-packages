# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.python import PythonPackage

from spack.package import *


class Clustcc(PythonPackage):
    """A distributed compiler frontend for C and C++ using MPI"""

    maintainers("JohnGouwar")
    git = "https://github.com/JohnGouwar/clustcc.git"

    version("main")

    depends_on("py-setuptools", type=("build"))
    depends_on("py-mpi4py", type=("build", "run"))
    depends_on("py-epic-ipc", type=("build", "run"))
    depends_on("python@3.9:", type=("build", "run"))

