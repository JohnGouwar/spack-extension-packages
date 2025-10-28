from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

class BuildSharedLibrary(build_ext):
    def build_extension(self, ext):
        ext_path = self.get_ext_fullpath(ext.name)

        compile_args = ext.extra_compile_args or []
        self.compiler.compile(
            ext.sources,
            output_dir=self.build_temp,
            extra_postargs=compile_args
        )

        # Get object file(s)
        objects = self.compiler.object_filenames(ext.sources, output_dir=self.build_temp)

        link_args = ext.extra_link_args or []
        # Link to shared object
        self.compiler.link_shared_object(
            objects,
            ext_path,
            extra_postargs=link_args
        )

setup(
    name="PosixMQ",
    packages=["PosixMQ"],
    ext_modules=[
        Extension(
            "PosixMQ.PosixMQ",
            sources=["PosixMQ/posixmq.c"],
            extra_link_args=["-lrt"]
        )
    ],
    cmdclass={
        'build_ext': BuildSharedLibrary
    }
)
