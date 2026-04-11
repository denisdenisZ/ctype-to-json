from parse_headers import HeaderParser
from generate_prober import generate_and_probe
from insert_platform_data import insert_platform_data

from pathlib import Path
import shutil
import argparse
import tomllib
import json
import sys


def main(header):
    include_dir = Path(header).resolve().parent
    tmp_dir = Path("./.tmp")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    parser = HeaderParser()
    data = parser.parse_header(header, ["-x", "c", "-std=c11"])
    result = generate_and_probe(data, header, include_dir, tmp_dir)

    output = insert_platform_data(result.stdout, data)
    print(json.dumps(output, indent=2))
    shutil.rmtree(tmp_dir, ignore_errors=True)


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


def write_json(data: dict, path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_config(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


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
        print(f"Config error: parser.c_standard '{cstd}' is not supported, allowed values are: 11, 99, 17")
        sys.exit(1)


def cleanup(debug: bool, tmp_dir: Path):
    if not debug:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def handle_no_probe(data: dict, out):
    if out is None:
        json.dumps(data, indent=2)
    else:
        write_json(data, out)


def main2(ctx):
    user_header = ctx["header"]
    config = ctx["config"]
    verify_config(config)

    tmp_dir = Path("./.tmp")
    shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    parser = HeaderParser()
    data = parser.parse_header(
        user_header, "-x", "c", resolve_std(config["c_standard"])
    )

    if ctx["no_probe"]:
        handle_no_probe(data, config["output"])
    if ctx["sizes"]:
        pass
    if ctx["emit_prober"]:
        pass

    cleanup(ctx["debug"], tmp_dir)


def setup():
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
    main2(ctx)


if __name__ == "__main__":
    setup()
