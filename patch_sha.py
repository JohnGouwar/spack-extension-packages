import re
from pathlib import Path
from hashlib import file_digest
from dataclasses import dataclass
import tarfile
SHA256_RE = re.compile(r'sha256="(\w*)"')

@dataclass
class SingleFile:
    file: str
@dataclass 
class Archive:
    archive_dirs: list[str]
    archive_file: str

PackageT = SingleFile | Archive

def patch_sha_for_package(package_name: str, pt: PackageT):
    REPO_PATH = Path(__file__).parent / "spack_repo" / "extensions" / "packages"
    package_path = REPO_PATH / package_name
    package_py_path = package_path / "package.py"
    if isinstance(pt, SingleFile):
        file_path = package_path / pt.file
        with open(file_path, "rb") as f:
            shasum = file_digest(f, "sha256").hexdigest()
    elif isinstance(pt, Archive):
        archive_paths = [package_path / ad for ad in pt.archive_dirs]
        archive_file_path = package_path / pt.archive_file
        with tarfile.open(archive_file_path, "w:gz") as f:
            for ap in archive_paths:
                f.add(ap, arcname=ap.name)
        with open(archive_file_path, "rb") as f:
            shasum = file_digest(f, "sha256").hexdigest()
    with open(package_py_path, "r") as f:
        original_text = f.read()
        new_text = re.sub(SHA256_RE, f'sha256="{shasum}"', original_text)
    with open(package_py_path, "w") as f:
        f.write(new_text)

if __name__ == "__main__":
    PACKAGES = {
        "tracing_compiler_wrapper": SingleFile("cc.sh"),
        "mqsend": SingleFile("mqsend.c"),
        "clustcc_compiler_wrapper": SingleFile("cc.sh"),
        "clustcc_client": SingleFile("client.c"),
        "py_epic_ipc": Archive(["src"], "epic_ipc.tar.gz"),
        "simple_c_package": SingleFile("simple.c")
    }
    for name, pt in PACKAGES.items():
        patch_sha_for_package(name, pt)
