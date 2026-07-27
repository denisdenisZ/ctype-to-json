import copy

from ctype_to_json.platform_data import insert_platform_data

BASE_DATA = {
    "meta": {"kind": "metadata", "headers": []},
    "ControlMode": {"name": "ControlMode", "kind": "enum", "fields": []},
    "Foo": {
        "name": "Foo",
        "kind": "struct",
        "fields": [
            {"name": "a", "kind": "field", "type": "int"},
            {"name": "b", "kind": "field", "type": "float"},
        ],
    },
}

STDOUT = (
    "Foo 8\n"
    "Foo.a 0\n"
    "Foo.a.size 4\n"
    "Foo.b 4\n"
    "Foo.b.size 4\n"
)


def test_inserts_struct_size_and_field_offsets():
    data = copy.deepcopy(BASE_DATA)

    result = insert_platform_data(STDOUT, data)

    assert result["Foo"]["size"] == 8
    fields = {f["name"]: f for f in result["Foo"]["fields"]}
    assert fields["a"] == {
        "name": "a", "kind": "field", "type": "int", "offset": 0, "size": 4
    }
    assert fields["b"] == {
        "name": "b", "kind": "field", "type": "float", "offset": 4, "size": 4
    }


def test_leaves_non_struct_entries_untouched():
    data = copy.deepcopy(BASE_DATA)

    result = insert_platform_data(STDOUT, data)

    assert result["ControlMode"] == BASE_DATA["ControlMode"]
    assert "meta" in result


def test_missing_probe_line_yields_none():
    data = copy.deepcopy(BASE_DATA)
    stdout = "Foo 8\nFoo.a 0\nFoo.a.size 4\n"

    result = insert_platform_data(stdout, data)

    b_field = next(f for f in result["Foo"]["fields"] if f["name"] == "b")
    assert b_field["offset"] is None
    assert b_field["size"] is None
