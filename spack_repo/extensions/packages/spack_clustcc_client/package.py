# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install spack-distcc-client
#
# You can edit this file again by typing:
#
#     spack edit spack-distcc-client
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

import pathlib
from spack_repo.builtin.build_systems.generic import Package
from spack.package import *


class SpackClustccClient(Package):
    """The client for masquerading clustcc calls"""

    # FIXME: Add a proper url for your package's homepage here.
    url = f"file:///{pathlib.PurePath(__file__).parent}/client.c"


    maintainers("JohnGouwar")

    version(
        "1.0",
        sha256="616ec98bf1c400c489ae073fb327b9e19b392aa3a50f485d016b92dcb4d9d849",
        expand=False
    )
    depends_on("c", type="build")

    def install(self, spec, prefix):
        client_src = pathlib.Path(self.stage.source_path) / "client.c"
        client_out = pathlib.Path(self.stage.source_path) / "clustcc_client"
        cc = which(env.get("CC", "CC_FAIL"), required=True)
        cc("-lrt", "-o", str(client_out), str(client_src))
        mkdir(prefix.bin)
        install(str(client_out), prefix.bin.clustcc_client)
