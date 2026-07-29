"""
libclang setup helpers.

Handles locating the system libclang.so, configuring cindex to use it,
and parsing a header file into a translation unit — all in one call.
"""

import subprocess

from clang import cindex

DEFAULT_CLANG_VERSION = "20"

_configured = False  # guards against calling Config.set_library_file() twice


def find_libclang(version=DEFAULT_CLANG_VERSION):
    """Locate the libclang.so shipped by apt for the given clang version."""
    candidates = (
        f"clang-{version}",
        f"libclang-{version}-dev",
        f"libclang1-{version}",
    )
    for pkg in candidates:
        try:
            out = subprocess.check_output(["dpkg", "-L", pkg], text=True)
        except subprocess.CalledProcessError:
            continue
        for line in out.splitlines():
            if "libclang" in line and "libclang-cpp" not in line and line.endswith(".so.1"):
                return line
    return None


def find_resource_dir(version=DEFAULT_CLANG_VERSION):
    """Ask clang directly for its resource dir (where stdbool.h etc. live)."""
    try:
        out = subprocess.check_output(
            [f"clang-{version}", "-print-resource-dir"], text=True)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def clang_init(version=DEFAULT_CLANG_VERSION):
    """Point cindex at the system libclang.so. Safe to call multiple times."""
    global _configured
    if _configured:
        return
    lib_path = find_libclang(version)
    if lib_path:
        cindex.Config.set_library_file(lib_path)
    _configured = True


def build_parse_args(version=DEFAULT_CLANG_VERSION, std="c99"):
    """Build the -I/-std args needed to parse plain C headers with this clang."""
    args = [f"-std={std}"]
    resource_dir = find_resource_dir(version)
    if resource_dir:
        args.append(f"-I{resource_dir}/include")
    args += ["-I/usr/local/include", "-I/usr/include"]
    return args


def parse_header(
        header_path,
        version=DEFAULT_CLANG_VERSION,
        std="c99",
        extra_args=None):
    """
    One-call entry point: configure libclang, parse header_path, return the
    translation unit. Diagnostics are printed but do not raise.
    """
    clang_init(version)
    index = cindex.Index.create()
    args = build_parse_args(version, std)
    if extra_args:
        args += extra_args

    tu = index.parse(header_path, args)
    for diag in tu.diagnostics:
        print(diag)
    return tu
