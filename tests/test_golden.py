"""End-to-end test that produces a complete JSON output exercising every
currently supported feature in a single struct: primitive types, bool,
enums, refs to both typedef'd and non-typedef'd structs, multi-field
nested structs, arrays of primitives and of refs, and pointers to both
a struct and a primitive.

The expected output is a golden file at fixtures/full_featured.json,
produced from fixtures/headers/full_featured.h.
"""
import json

import pytest

from ctype_to_json.parser import HeaderParser
from ctype_to_json.prober import generate_and_probe
from ctype_to_json.platform_data import insert_platform_data


def test_full_pipeline_produces_json_with_every_supported_feature(
    fixtures_dir, headers_dir, tmp_path, has_gcc
):
    if not has_gcc:
        pytest.skip("gcc not available")

    expected = json.loads((fixtures_dir / "full_featured.json").read_text())

    header = headers_dir / "full_featured.h"
    parser = HeaderParser()
    data = parser.parse_headers([str(header)], ["-x", "c", "-std=c11"])

    result = generate_and_probe(data, [str(header)], [], tmp_path, "gcc", [])
    assert result.returncode == 0

    output = insert_platform_data(result.stdout, data)
    output.pop("meta")

    assert output == expected
