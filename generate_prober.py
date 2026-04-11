import json
import subprocess
import sys
from pathlib import Path

template = """
#include <stddef.h>
#include <stdio.h>
{headers}

int main(void) {{
{prints}
}}
"""

print_size_template = (
    'printf("{struct_name} %lu\\n",'
    ' sizeof({struct_name}));\n'
)

print_offset_template = (
    'printf("{struct_name}.{field_name} %d\\n",'
    ' offsetof({struct_name}, {field_name}));\n'
)

print_field_size_template = (
    'printf("{struct_name}.{field_name}.size %lu\\n",'
    ' sizeof((({struct_name}*)0)->{field_name}));\n'
)


def probe(bin: str):
    data = subprocess.run(bin, capture_output=True, text=True)
    return data


def compile(
        src: str,
        out_dir: str,
        compiler: str = "gcc",
        flags: list[str] = [],
        include_dirs: list[str] = []):
    src = Path(src)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bin = out_dir / src.stem
    cmd = [
        compiler,
        *[f"-I{d}" for d in include_dirs],
        *flags,
        str(src),
        "-o", str(bin)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
        sys.exit(1)
    return bin


def fill_template(data: dict, header_files: list[str]):
    offsets = []
    sizes = []
    includes = "\n".join(
        f'#include "{Path(h).resolve()}"' for h in header_files
    )
    for key, value in data.items():
        if value["kind"] == "struct":
            sizes.append(print_size_template.format(struct_name=key))
            for field in value["fields"]:
                offsets.append(
                    print_offset_template.format(
                        struct_name=key, field_name=field["name"]
                    ))
                sizes.append(print_field_size_template.format(
                    struct_name=key, field_name=field["name"]
                ))

    result = template.format(prints="".join(offsets + sizes), headers=includes)
    return result


def generate_prober(
        data: dict,
        header_files: list[str],
        include_dirs: list[str],
        out_dir: str,
        compiler: str = "gcc",
        flags: list[str] = []):

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prober_c = out_dir / "size_prober.c"

    result = fill_template(data, header_files)

    with open(prober_c, "w", encoding="utf-8") as f:
        f.write(result)
    return compile(
        str(prober_c), str(out_dir), compiler, flags, include_dirs
    )


def generate_prober_from_file(
        header_files: list[str],
        json_file: str,
        include_dirs: list[str],
        out_dir: str,
        compiler: str = "gcc",
        flags: list[str] = []):

    with open(json_file) as f:
        data = json.load(f)

    generate_prober(data, header_files, include_dirs, out_dir, compiler, flags)


def generate_and_probe(
        data: dict,
        header_files: list[str],
        include_dirs: list[str],
        out_dir: str,
        compiler: str = "gcc",
        flags: list[str] = []):
    return probe(
        generate_prober(
            data,
            header_files,
            include_dirs,
            out_dir,
            compiler,
            flags
        )
    )
