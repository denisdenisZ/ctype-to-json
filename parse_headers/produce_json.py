from parse_headers import HeaderParser
from generate_prober import generate_and_probe
from insert_platform_data import insert_platform_data

from pathlib import Path
import sys
import shutil
import json


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


if __name__ == "__main__":
    main(sys.argv[1])
