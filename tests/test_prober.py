import pytest

from ctype_to_json.parser import HeaderParser
from ctype_to_json.prober import fill_template, generate_and_probe, emit_prober_source
from ctype_to_json.platform_data import insert_platform_data

STRUCT_DATA = {
    "Foo": {
        "name": "Foo",
        "kind": "struct",
        "fields": [{"name": "a", "kind": "field", "type": "int"}],
    },
    "SomeEnum": {"name": "SomeEnum", "kind": "enum", "fields": []},
}


def test_fill_template_emits_size_and_offset_prints_for_structs_only():
    source = fill_template(STRUCT_DATA, ["my_types.h"])

    assert '#include "' in source
    assert "my_types.h" in source
    assert 'sizeof(Foo)' in source
    assert 'offsetof(Foo, a)' in source
    assert "SomeEnum" not in source


def test_emit_prober_source_writes_named_file(tmp_path):
    prober_path = emit_prober_source(STRUCT_DATA, ["my_types.h"], tmp_path, "out_prober.c")

    assert prober_path == tmp_path / "out_prober.c"
    assert prober_path.exists()
    assert "sizeof(Foo)" in prober_path.read_text()


@pytest.mark.usefixtures("has_gcc")
def test_generate_and_probe_matches_real_offsets(headers_dir, tmp_path, has_gcc):
    if not has_gcc:
        pytest.skip("gcc not available")

    header = headers_dir / "test_header.h"
    parser = HeaderParser()
    data = parser.parse_headers([str(header)], ["-x", "c", "-std=c11"])

    result = generate_and_probe(
        data, [str(header)], [str(headers_dir)], tmp_path, "gcc", []
    )
    assert result.returncode == 0

    output = insert_platform_data(result.stdout, data)

    assert output["ValueRange"]["size"] == 12
    fields = {f["name"]: f for f in output["ValueRange"]["fields"]}
    assert fields["min_us"] == {
        "name": "min_us", "kind": "field", "type": "uint32_t",
        "offset": 0, "size": 4,
    }
    assert fields["max_us"]["offset"] == 4
    assert fields["step_us"]["offset"] == 8

    assert output["window"]["size"] == 8
