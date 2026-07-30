#!/usr/bin/env python3

import sys
import json

from predicates import (
    is_top_level_record_or_enum_def,
)

from handlers import (
    dispatch_top_level,
    dispatch_field,
)
from prints import print_all_attributes
from libclang_init import parse_header

# Always gets a valid type, either typedef or declared, useful for codegen
# print(cursor.type.spelling)

'''
Field types:
1. bitfield
2. standard numeric
3. fixed width
4. pointer
5. array
6. nested
7. bool
'''


def should_add_type(name, node, types):
    category = types.get(node["kind"])
    if category is None:
        return False
    return name not in category


def walk(tu):
    out = {
        "target": {},
        "struct": {},
        "union": {},
        "enum": {},
        "numeric": {},
        "complex": {},
        "bool": {},

        "pointer": {},
        "func_pointer": {},
        "array": {},
    }
    for child in tu.cursor.get_children():

        if not is_top_level_record_or_enum_def(child):
            continue

        parent = dispatch_top_level(child)
        name, parent = list(parent.items())[0]
        out[parent["kind"]][name] = parent

        for field in child.get_children():
            # FIXME: Handle error
            nodes = dispatch_field(field)
            if not nodes:
                continue

            for field_name, field_node in nodes.items():
                if should_add_type(name, field_node, out):
                    out[field_node["kind"]][field_name] = field_node

    return out


def walk_print(tu):
    for child in tu.cursor.get_children():

        if not is_top_level_record_or_enum_def(child):
            continue

        print_all_attributes(child)

        for field in child.get_children():
            print_all_attributes(field)


def main():
    header_path = sys.argv[1]
    cstd = sys.argv[2]
    output_type = sys.argv[3]

    tu = parse_header(
        header_path,
        version=20,
        std=cstd,
    )

    for diag in tu.diagnostics:
        print(diag)

    if output_type == "json":
        print(json.dumps(walk(tu), indent=2))
    elif output_type == "txt":
        walk_print(tu)


main()
