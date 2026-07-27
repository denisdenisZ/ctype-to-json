import pytest

from ctype_to_json.parser import HeaderParser


def parse(headers_dir, *names, skip_unsupported=False, std="c11"):
    parser = HeaderParser(skip_unsupported=skip_unsupported)
    paths = [str(headers_dir / name) for name in names]
    return parser.parse_headers(paths, ["-x", "c", f"-std={std}"])


def test_primitive_and_typedef_struct_fields(headers_dir):
    data = parse(headers_dir, "test_header.h")

    control_config = data["ControlConfig"]
    assert control_config["kind"] == "struct"
    field_names = [f["name"] for f in control_config["fields"]]
    assert field_names == [
        "mode", "target_value", "value_us", "scale_db",
        "value_range", "scale_range", "enabled", "update_speed",
    ]


def test_bool_field_detected_by_source_text(headers_dir):
    data = parse(headers_dir, "test_header.h")

    enabled = next(
        f for f in data["ControlConfig"]["fields"] if f["name"] == "enabled"
    )
    assert enabled["type"] == "bool"


def test_ref_to_typedef_struct(headers_dir):
    data = parse(headers_dir, "test_header.h")

    mode_field = next(
        f for f in data["ControlConfig"]["fields"] if f["name"] == "mode"
    )
    assert mode_field["type"] == "ControlMode"
    assert mode_field["ref"] == "ControlMode"
    assert "ControlMode" in data


def test_non_typedef_struct_uses_struct_prefixed_key(headers_dir):
    data = parse(headers_dir, "test_header.h")

    assert "struct RegionRect" in data
    assert data["struct RegionRect"]["name"] == "RegionRect"

    roi_field = next(
        f for f in data["DeviceConfig"]["fields"] if f["name"] == "roi"
    )
    assert roi_field["ref"] == "struct RegionRect"


def test_array_fields_including_multidimensional(headers_dir):
    data = parse(headers_dir, "test_header.h")
    fields = {f["name"]: f for f in data["FilterConfig"]["fields"]}

    assert fields["gains"]["array"] == [5]
    assert fields["gains2d"]["array"] == [5, 4]
    assert fields["gains3d"]["array"] == [5, 4, 3]
    assert "ref" not in fields["gains"]

    filter_table = fields["filter_table"]
    assert filter_table["array"] == [5]
    assert filter_table["ref"] == "FilterMode"


def test_pointer_field(headers_dir):
    data = parse(headers_dir, "test_header.h")

    pointer_field = next(
        f for f in data["DeviceConfig"]["fields"] if f["name"] == "pointer"
    )
    assert pointer_field["pointer"] is True
    assert pointer_field["type"] == "FilterConfig"
    assert pointer_field["ref"] == "FilterConfig"


def test_enum_fields(headers_dir):
    data = parse(headers_dir, "test_header.h")

    control_mode = data["ControlMode"]
    assert control_mode["kind"] == "enum"
    assert control_mode["fields"][0] == {
        "name": "CONTROL_MODE_AUTO", "type": "int", "value": 0
    }
    assert control_mode["fields"][-1]["value"] == 3


def test_shared_include_is_only_processed_once(headers_dir):
    data = parse(headers_dir, "test_header.h", "test_header2.h")

    assert "window" in data
    window_field = next(
        f for f in data["some_fucking_struct"]["fields"]
        if f["name"] == "window"
    )
    assert window_field["ref"] == "window"


def test_metadata_lists_headers_without_duplicates(headers_dir):
    data = parse(headers_dir, "test_header.h", "test_header2.h")

    headers = data["meta"]["headers"]
    assert headers.count(str(headers_dir / "window_cfg.h")) == 1


def test_bitfield_is_unsupported_and_exits(headers_dir):
    with pytest.raises(SystemExit) as exc_info:
        parse(headers_dir, "test_header_bad.h")
    assert exc_info.value.code == 1


def test_bitfield_skipped_with_skip_unsupported(headers_dir):
    data = parse(headers_dir, "test_header_bad.h", skip_unsupported=True)

    assert "bad_struct" not in data


def test_union_field_is_unsupported_and_exits(headers_dir):
    with pytest.raises(SystemExit):
        parse(headers_dir, "unsupported_union.h")


def test_union_field_skipped_with_skip_unsupported(headers_dir):
    data = parse(headers_dir, "unsupported_union.h", skip_unsupported=True)

    assert "struct_with_union_field" not in data


def test_taint_propagates_to_referencing_structs(headers_dir):
    data = parse(headers_dir, "taint_propagation.h", skip_unsupported=True)

    assert "struct_with_union_field" not in data
    assert "wraps_unsupported" not in data
