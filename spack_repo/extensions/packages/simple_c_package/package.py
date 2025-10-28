# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import pathlib
from spack_repo.builtin.build_systems.generic import Package

from spack.package import *


class SimpleCPackage(Package):
    """This package is a good smoke test when hacking around with compilers"""
    url = f"file:///{pathlib.PurePath(__file__).parent}/simple.c"
    # FIXME: Add proper versions here.
    version(
        "1.0",
        sha256="9f66edc1548f9281ed73fe31e1d396f57cb40b4b46e461072e2e884fe562a837",
        expand=False
    )

    depends_on("c")

    def install(self, spec, prefix):
        src = pathlib.Path(self.stage.source_path) / "simple.c"
        out = pathlib.Path(self.stage.source_path) / "simple"
        cc = which(env.get("CC", "CC_FAIL"), required=True)
        cc("-o", str(out), str(src))
        mkdir(prefix.bin)
        install(str(out), prefix.bin.simple)
