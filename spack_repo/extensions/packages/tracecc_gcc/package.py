import pathlib
import os
from spack_repo.builtin.build_systems.generic import Package
from spack_repo.builtin.build_systems.compiler import CompilerPackage
from spack_repo.builtin.packages.gcc.package import Gcc
from spack.package import *

class TraceccGcc(Package, CompilerPackage):
    # Thin wrapper, scripts are generated during `install`
    has_code = False
    phases = ["install"]
    # have to pick names that the compiler-wrapper already knows
    compiler_languages = ["c", "c++"]
    c_names = ["cc"]
    cxx_names = ["c++"]
    compiler_wrapper_link_paths = {
        "c": os.path.join("cc"),
        "cxx": os.path.join("c++")
    }
    # These should just pass through from GCC
    debug_flags = Gcc.debug_flags
    opt_flags = Gcc.opt_flags
    implicit_rpath_libs = Gcc.implicit_rpath_libs
    stdcxx_libs = Gcc.stdcxx_libs
    
    provides("c", "cxx")
    depends_on("tracecc-client")
    # TODO: External GCC can have versions that are not defined by the package
    # Example: Fedora 41 has gcc@14.3.1, but this is not in the GCC package
    for ver, args in Gcc.versions.items():
        version(f"{ver}")
        depends_on(f"gcc@{ver} languages=c,c++", when=f"@{ver}", type=("run"))

    @classmethod
    def runtime_constraints(cls, *, spec, pkg):
        return Gcc.runtime_constraints(spec=spec, pkg=pkg)

    def _cc_path(self) -> Optional[str]:
        return str(self.spec.prefix.bin.cc)

    def _cxx_path(self) -> Optional[str]:
        return os.path.join(self.spec.prefix.bin, "c++")

    def archspec_name(self) -> str:
        return "gcc"

    def _standard_flag(self, *, language: str, standard: str) -> str:
        return self.spec["gcc"].package._standard_flag(language=language, standard=standard)

    def setup_dependent_build_environment(self, env: EnvironmentModifications, dependent_spec: Spec) -> None:
        env.set("SPACK_TRACE_SPEC_HASH", dependent_spec.dag_hash())
        
    def setup_run_environment(self, env) -> None:
        if self.cc:
            env.set("CC", self.cc)
        if self.cxx:
            env.set("CXX", self.cxx)

    def install(self, spec, prefix):
        mkdir(prefix.bin)
        real_c_compiler = spec["gcc"].package.cc
        real_cxx_compiler = spec["gcc"].package.cxx
        tracecc_client = spec["tracecc-client"].prefix.bin.tracecc_client
        wrapped_c_script = (
            f'#!/bin/sh\n{tracecc_client} "$SPACK_TRACE_SPEC_HASH" {real_c_compiler} "$@"'
        )
        wrapped_cxx_script = (
            f'#!/bin/sh\n{tracecc_client} "$SPACK_TRACE_SPEC_HASH" {real_cxx_compiler} "$@"'
        )
        wrapped_c_path = pathlib.Path(self.stage.source_path) / "cc"
        wrapped_cxx_path = pathlib.Path(self.stage.source_path) / "c++"
        with open(wrapped_c_path, "w") as f:
            f.write(wrapped_c_script)
        with open(wrapped_cxx_path, "w") as f:
            f.write(wrapped_cxx_script)
        install(str(wrapped_c_path), prefix.bin.cc)
        os.chmod(prefix.bin.cc, 0o755)
        install(str(wrapped_cxx_path), os.path.join(prefix.bin, "c++"))
        os.chmod(os.path.join(prefix.bin, "c++"), 0o755)

