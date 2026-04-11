from parse_headers import HeaderParser
from generate_prober import generate_and_probe
from generate_prober import generate_prober
from insert_platform_data import insert_platform_data

from pathlib import Path
import shutil
import argparse
import tomllib
import json
import sys


def pares_args():
    parser = argparse.ArgumentParser(
        description="Serializer of C data types to json"
    )
    parser.add_argument(
        "header",
        metavar="header_file.h",
        help="The header to parse"
    )
    parser.add_argument(
        "--config",
        "-c",
        metavar="FILE",
        help="Path to config file"
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--DEBUG",
        action="store_true",
        help="Enables debug output"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--emit-prober",
        action="store_true",
        help="Emits the prober instead of running it locally"
    )
    group.add_argument(
        "--sizes",
        metavar="FILE",
        help="Takes an already generated sizes file"
    )
    group.add_argument(
        "--no-probe",
        action="store_true",
        help="Skips size and offset probing, does not generate prober"
    )
    return parser.parse_args()


def is_std_allowed(cstd: str):
    allowed = ["11", "99", "17"]
    return cstd in allowed


def resolve_std(cstd: str):
    return f"-std=c{cstd}"


def verify_config(config: dict):
    toolchain = config.get("toolchain", {})
    parser = config.get("parser", {})

    cc = toolchain.get("cc")
    if cc is None:
        print("Config error: toolchain.cc is required")
        sys.exit(1)

    cstd = parser.get("c_standard")
    if cstd is not None and not is_std_allowed(cstd):
        print(
            f"Config error: parser.c_standard '{cstd}' is not supported, "
            f"allowed values are: 11, 99, 17"
        )
        sys.exit(1)


def write_json(data: dict, path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_config(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


class Pipeline:
    def __init__(self, ctx: dict):
        self.header = ctx["header"]
        self.config = ctx["config"] or {}
        self.out = ctx["out"]
        self.emit_prober = ctx["emit_prober"]
        self.no_probe = ctx["no_probe"]
        self.sizes = ctx["sizes"]
        self.debug = ctx["debug"]
        self.tmp_dir = Path("./.tmp")
        toolchain = self.config.get("toolchain", {})
        self.compiler = toolchain.get("cc", "gcc")
        self.flags = toolchain.get("flags", [])
        self.include_dirs = toolchain.get("include_dirs", [])
        self.include_dirs.append(str(Path(self.header).resolve().parent))

    def _setup(self):
        verify_config(self.config)

        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        parser = HeaderParser()
        self.data = parser.parse_header(
            self.header,
            ["-x", "c", resolve_std(self.config["parser"]["c_standard"])]
        )

    def _cleanup(self):
        if not self.debug:
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def run(self):
        self._setup()
        if self.no_probe:
            self._handle_no_probe()
        elif self.sizes:
            self._handle_sizes()
            pass
        elif self.emit_prober:
            self._handle_emit_prober()
        else:
            self._handle_normal()
        self._cleanup()

    def _handle_no_probe(self):
        if self.out is None:
            print(json.dumps(self.data, indent=2))
        else:
            write_json(self.data, self.out)

    def _handle_emit_prober(self):
        out = self.out if self.out is not None else "."
        generate_prober(
            self.data,
            self.header,
            self.include_dirs,
            out
        )
        print(
            f"Prober written to '{out}'.\n"
            f"Run it on the target machine and pass the output back with:\n"
            f"produce_json.py --config <config_file> {self.header}"
            " --sizes <output_file>"
        )
        sys.exit(0)

    def _handle_sizes(self):
        with open(self.sizes) as f:
            stdout = f.read()
        output = insert_platform_data(stdout, self.data)
        if self.out is None:
            print(json.dumps(output, indent=2))
        else:
            write_json(output, self.out)

    def _handle_normal(self):
        result = generate_and_probe(
            self.data,
            self.header,
            self.include_dirs,
            self.tmp_dir,
            self.compiler,
            self.flags
        )
        output = insert_platform_data(result.stdout, self.data)
        if self.out is None:
            print(json.dumps(output, indent=2))
        else:
            write_json(output, self.out)


def init():
    args = pares_args()
    config = load_config(args.config) if args.config is not None else None
    ctx = {
        "header": args.header,
        "config": config,
        "out": args.output,
        "emit_prober": args.emit_prober,
        "no_probe": args.no_probe,
        "sizes": args.sizes,
        "debug": args.DEBUG,
    }
    if ctx["debug"]:
        print(f"Header: {args.header}")
        print(f"Config: {config}")
        print(f"Output: {args.output}")
        print(f"Emit prober: {args.emit_prober}")
        print(f"No probe: {args.no_probe}")
        print(f"Sizes: {args.sizes}")
    Pipeline(ctx).run()


if __name__ == "__main__":
    init()
