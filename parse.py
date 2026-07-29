#!/usr/bin/env python3

import sys

from predicates import (
    get_cursor_type,
    is_bool,
    is_complex,
    is_enum,
    is_numeric,
    is_struct,
    is_union,
    is_array,
    is_pointer,
    is_bitfield,
    is_top_level_record_or_enum_def,
)
from handlers import (
    handle_bitfield,
    handle_pointer,
    handle_func_ptr,
    handle_struct,
    handle_union,
    handle_enum,
    handle_bool,
    handle_array,
    handle_complex,
    handle_numeric,
    handle_top_level_struct,
    handle_top_level_enum,
    handle_top_level_union,
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

FIELD_DISPATCH = [
    (is_bitfield, handle_bitfield),
    (is_pointer,  handle_pointer),
    (is_array,    handle_array),
    (is_bool,     handle_bool),
    (is_enum,     handle_enum),
    (is_struct,   handle_struct),
    (is_union,    handle_union),
    (is_complex,  handle_complex),
    (is_numeric,  handle_numeric),
]

TOP_LEVEL_DISPATCH = [
    (is_struct, handle_top_level_struct),
    (is_enum, handle_top_level_enum),
    (is_union, handle_top_level_union),
]


def walk(tu):
    for child in tu.cursor.get_children():
        fields = []

        if not is_top_level_record_or_enum_def(child):
            continue

        print_all_attributes(child)

        parent = dispatch_top_level(child)

        for field in child.get_children():
            # FIXME: Handle error
            node = dispatch_field(field)

            fields.append(node)
            print_all_attributes(field)


def dispatch(cursor, dispatch_list):
    for predicate, handler in dispatch_list:
        if predicate(cursor):
            return handler(cursor)
    # FIXME: Return better error
    return False


def dispatch_top_level(cursor):
    out = dispatch(cursor, TOP_LEVEL_DISPATCH)
    # FIXME: Return better error
    return out if out else False


def dispatch_field(field):
    out = dispatch(field, FIELD_DISPATCH)
    # FIXME: Return better error
    return out if out else False


def handle_node(node):
    pass


def main():
    header_path = sys.argv[1]
    cstd = sys.argv[2]

    tu = parse_header(
        header_path,
        version=20,
        std=cstd,
    )

    for diag in tu.diagnostics:
        print(diag)

    walk(tu)


main()
