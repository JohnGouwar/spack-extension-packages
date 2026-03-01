import os
from spack.package import *
import spack_repo.builtin.packages.llvm.package as llvm_module
from spack_repo.builtin.packages.llvm.package import Llvm as BuiltinLlvm

# Various runtimes LLVM builds need access to 
def _get_gcc_install_dir_flag(spec, compiler):
    if not spec.satisfies("@16:"):
        return None
    gcc = Executable(spec["gcc"].package.cc)
    libgcc_path = gcc("-print-file-name=libgcc.a", output=str, fail_on_error=False).strip()
    if not os.path.isabs(libgcc_path):
        return None
    libgcc_dir = os.path.dirname(libgcc_path)
    return f"--gcc-install-dir={libgcc_dir}" if os.path.exists(libgcc_dir) else None

llvm_module.get_gcc_install_dir_flag = _get_gcc_install_dir_flag


class Llvm(BuiltinLlvm):
    pass
