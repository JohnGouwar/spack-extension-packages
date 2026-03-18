# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import pathlib
from spack_repo.builtin.build_systems.generic import Package
from spack.package import *


class ClustccClient(Package):
    """The client for masquerading clustcc calls"""

    # FIXME: Add a proper url for your package's homepage here.
    url = f"file:///{pathlib.PurePath(__file__).parent}/client.c"


    maintainers("JohnGouwar")

    version(
        "1.0",
        sha256="8d23547b2620ead63b982174bc05c88ef567af9be0599c947acff47ca0d8c2d2",
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



