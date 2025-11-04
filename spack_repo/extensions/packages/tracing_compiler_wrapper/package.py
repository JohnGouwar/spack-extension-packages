# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import pathlib
import sys

from spack_repo.builtin.packages.compiler_wrapper.package import CompilerWrapper

from spack.package import *


class TracingCompilerWrapper(CompilerWrapper):
    """ Provides the compiler wrapper for use with spack trace
    """

    url = f"file:///{pathlib.PurePath(__file__).parent}/cc.sh"
    if sys.platform != "win32":
        version(
            "3.0",
            sha256="0a170eda363cca4e6abaf3bfba9594b356db317fe80909ec8779f970fe89364f",
            expand=False,
        )
        # Dependency actually needed for tracing
        depends_on("mqsend", type=("build", "link", "run"))

    def setup_dependent_build_environment(self, env: EnvironmentModifications, dependent_spec: Spec) -> None:
        env.set("SPACK_TRACE_SPEC_HASH", dependent_spec.dag_hash())
        return super().setup_dependent_build_environment(env, dependent_spec)
