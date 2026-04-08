import json
import subprocess
import sys
from pathlib import Path

template = """
#include <stddef.h>
#include <stdio.h>
#include "{header}"

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


def generate_prober(
        data: dict,
        header_file: str,
        include_dir: str,
        out_dir: str):

    offsets = []
    sizes = []

    for key, value in data.items():
        if value["kind"] == "struct":
            sizes.append(print_size_template.format(struct_name=value["name"]))
            for field in value["fields"]:
                offsets.append(
                    print_offset_template.format(
                        struct_name=value["name"], field_name=field["name"]
                    ))
                sizes.append(print_field_size_template.format(
                    struct_name=value["name"], field_name=field["name"]
                ))

    result = template.format(
        prints="".join(offsets + sizes), header=header_file)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prober_c = out_dir / "size_prober.c"
    prober_bin = out_dir / "size_prober"

    with open(prober_c, "w", encoding="utf-8") as f:
        f.write(result)

    result = subprocess.run([
        "gcc",
        "-I", include_dir,
        str(prober_c),
        "-o", str(prober_bin)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
        sys.exit(1)

    return prober_bin


def generate_prober_from_file(
        header_file: str,
        json_file: str,
        include_dir: str,
        out_dir: str):

    with open(json_file) as f:
        data = json.load(f)

    generate_prober(data, header_file, include_dir, out_dir)


def generate_and_probe(
        data: dict,
        header_file: str,
        include_dir: str,
        out_dir: str):
    return probe(generate_prober(data, header_file, include_dir, out_dir))
