#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

ubuntu_arch_dict = {
    "x86_64": "amd64",
    "x86": "i386",
    "armv7hf": "armhf"
}

class LibiioConan(ConanFile):
    name = "libiio"
    version = "0.15"
    description = "libiio is used to interface to the Linux Industrial Input/Output (IIO) Subsystem"
    url = "https://github.com/bincrafters/conan-libname"
    homepage = "https://github.com/analogdevicesinc/libiio"
    author = "Eric Hargitt <eric.hargitt@gmail.com>"
    license = "LGPL"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    requires = (
        "flex/2.6.4@bincrafters/stable",
        "bison/3.0.4@bincrafters/stable",
        "libxml2/2.9.8@bincrafters/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        pack_names = []
        if tools.os_info.linux_distro == "ubuntu":
            pack_names = ["libcdk5-dev"]
            arch = ubuntu_arch_dict[self.settings.arch]
            pack_names = [item+':'+arch for item in pack_names]
            if not arch in ["amd64", "i386"]:
                self.run(r'sudo sed -i "s/^deb /deb \[arch=$(dpkg --print-architecture),i386] /" /etc/apt/sources.list')
                for url, repo in [("archive", ""), ("archive", "-updates"), ("security", "-security")]:
                    self.run(r'sudo echo \
                    "deb [arch={0}] http://{1}.ubuntu.com/ubuntu/ $(lsb_release -sc){2} main restricted universe multiverse" \
                    >> /etc/apt/sources.list'.format(arch, url, repo))
                self.run('dpkg --add-architecture {}'.format(arch))

        if pack_names:
            installer = tools.SystemPackageTool()
            installer.install(" ".join(pack_names)) # Install the package

    def source(self):
        source_url = "https://github.com/analogdevicesinc/libiio"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
