#!/usr/bin/env python3
import sys
from typing import Type
import clang.cindex as cindex
import subprocess

# pip install libclang
# If libclang.so isn't auto-found, uncomment and set the path:
# cindex.Config.set_library_file("/usr/lib/llvm-18/lib/libclang.so")

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

NUMERI_KINDS = (
    cindex.TypeKind.CHAR_S,
    cindex.TypeKind.SCHAR,
    cindex.TypeKind.UCHAR,

    cindex.TypeKind.SHORT,
    cindex.TypeKind.USHORT,

    cindex.TypeKind.INT,
    cindex.TypeKind.UINT,

    cindex.TypeKind.LONG,
    cindex.TypeKind.LONGLONG,
    cindex.TypeKind.ULONG,
    cindex.TypeKind.ULONGLONG,

    cindex.TypeKind.FLOAT,
    cindex.TypeKind.DOUBLE,
    cindex.TypeKind.LONGDOUBLE,
)


# ==================================================================
def print_all_children(cursor):
    for child in cursor.get_children():
        print(cursor.spelling)
        print(child.kind, child.spelling)
        print(child.type.spelling)
        print(child.type.get_canonical().kind)
        print()


def print_all_attributes(cursor):
    print("spelling:      ", cursor.spelling)
    print("displayname:   ", cursor.displayname)
    print("kind:          ", cursor.kind)
    print("type.spelling: ", cursor.type.spelling)
    print("type.kind:     ", cursor.type.kind)
    print("canonical type:", cursor.type.get_canonical().spelling)
    print("canonical kind:", cursor.type.get_canonical().kind)
    print("location:      ", cursor.location)
    print("extent:        ", cursor.extent)
    print("is_definition: ", cursor.is_definition())
    print("storage_class: ", cursor.storage_class)
    print("access_spec:   ", cursor.access_specifier)
    print("linkage:       ", cursor.linkage)
    print("is_bitfield:   ", cursor.is_bitfield())
    if cursor.is_bitfield():
        print("bitfield_width:", cursor.get_bitfield_width())
    print("semantic parent:", cursor.semantic_parent.spelling if cursor.semantic_parent else None)
    print("lexical parent: ", cursor.lexical_parent.spelling if cursor.lexical_parent else None)
    print("hash:          ", cursor.hash)
    print("USR:           ", cursor.get_usr())
    print()
    print()

# ==================================================================


def get_cursor_type(cursor):
    return cursor.type.get_canonical()


def is_pointer(cursor):
    return get_cursor_type(cursor).kind == cindex.TypeKind.POINTER


def resolve_pointer(cursor):
    return get_cursor_type(cursor).get_pointee().get_canonical()


def resolve_if_pointer(t):
    if t.kind == cindex.TypeKind.POINTER:
        return t.get_pointee().get_canonical()
    return t


def is_func_ptr(cursor):
    t = resolve_if_pointer(get_cursor_type(cursor))
    return t.kind == cindex.TypeKind.FUNCTIONPROTO


def pointer_depth(cursor):
    depth = 0
    t = get_cursor_type(cursor)
    while t.kind == cindex.TypeKind.POINTER:
        t = t.get_pointee().get_canonical()
        depth += 1
    return depth


def is_array(cursor):
    kind = get_cursor_type(cursor).kind
    return kind in (
        cindex.TypeKind.CONSTANTARRAY,
        cindex.TypeKind.INCOMPLETEARRAY,
        cindex.TypeKind.VARIABLEARRAY,
    )


def is_enum(cursor):
    t = get_cursor_type(cursor)
    return t.kind == cindex.TypeKind.ENUM


def is_struct(cursor):
    t = get_cursor_type(cursor)
    return t.kind == cindex.TypeKind.RECORD and t.get_declaration().kind == cindex.CursorKind.STRUCT_DECL


def is_union(cursor):
    t = get_cursor_type(cursor)
    return t.kind == cindex.TypeKind.RECORD and t.get_declaration().kind == cindex.CursorKind.UNION_DECL


def is_bool(cursor):
    return cursor.type.get_canonical().kind == cindex.TypeKind.BOOL


def is_numeric(cursor):
    return get_cursor_type(cursor).kind in NUMERI_KINDS


def is_complex(cursor):
    return get_cursor_type(cursor).kind == cindex.TypeKind.COMPLEX


def get_unique_top_level_definitions(tu, kind):
    out = []
    # Only top level to avoid nested structs/enums
    for cursor in tu.cursor.get_children():
        if cursor.location.is_in_system_header:
            continue
        # Must be definition to collapse forward-declared + defined into one
        if cursor.kind == kind and cursor.is_definition():
            # Skips anonymous ones with no usable name
            if cursor.spelling != "":
                out.append(cursor)
    return out


def is_top_level_enum_union_struct_definition(cursor):
    kinds = (cindex.CursorKind.STRUCT_DECL, cindex.CursorKind.ENUM_DECL, cindex.CursorKind.UNION_DECL)
    if cursor.kind not in kinds:
        return False
    if cursor.location.is_in_system_header:
        return False
    if not cursor.is_definition():
        return False
    if cursor.spelling == "":
        return False
    if cursor.semantic_parent.kind != cindex.CursorKind.TRANSLATION_UNIT:
        return False
    return True


def get_unique_top_level_struct_definitions(tu):
    return get_unique_top_level_definitions(tu, cindex.CursorKind.STRUCT_DECL)


def get_unique_top_level_enum_definitions(tu):
    return get_unique_top_level_definitions(tu, cindex.CursorKind.ENUM_DECL)


def get_unique_top_level_union_definitions(tu):
    return get_unique_top_level_definitions(tu, cindex.CursorKind.ENUM_UNION)


def print_all_cursors_top_level(tu):
    for cursor in tu.cursor.get_children():
        if cursor.location.is_in_system_header:
            continue
        print(cursor.kind, cursor.spelling)


def print_all_struct_definitions(tu):
    for cursor in tu.cursor.get_children():
        if cursor.location.is_in_system_header:
            continue
        if cursor.kind == cindex.CursorKind.STRUCT_DECL and cursor.is_definition():
            print(cursor.kind, cursor.spelling)
            print(cursor.type.spelling)


def print_all_enum_definitions(tu):
    for cursor in tu.cursor.get_children():
        if cursor.location.is_in_system_header:
            continue
        if cursor.kind == cindex.CursorKind.ENUM_DECL and cursor.is_definition():
            print(cursor.kind, cursor.spelling)


def print_all_struct_children(tu):
    structs = get_unique_top_level_struct_definitions(tu)
    for struct in structs:
        print_all_children(struct)


def walk(tu):
    for child in tu.cursor.get_children():
        if not is_top_level_enum_union_struct_definition(child):
            continue
        for field in child.get_children():
            isBitfield = field.is_bitfield()
            isPtr = is_pointer(field)
            isArr = is_array(field)
            isBoolean = is_bool(field)
            isEnumerator = is_enum(field)
            isStruct = is_struct(field)
            isUnion = is_union(field)
            isNumeric = is_numeric(field)
            isComplex = is_complex(field)

            states = [
                isBitfield, isPtr, isArr,
                isBoolean, isEnumerator, isStruct,
                isUnion, isNumeric, isComplex
            ]

            if not any(states):
                print()
                print()
                print()
                print("UNRECOGNIZED TYPE DETETCTED")
                print()
                print()
                print()
            print_all_attributes(field)


def find_libclang(version="20"):
    for pkg in (f"clang-{version}", f"libclang-{version}-dev", f"libclang1-{version}"):
        try:
            out = subprocess.check_output(["dpkg", "-L", pkg], text=True)
        except subprocess.CalledProcessError:
            continue
        for line in out.splitlines():
            if "libclang" in line and "libclang-cpp" not in line and line.endswith(".so.1"):
                return line
    return None


def clang_init():
    lib_path = find_libclang("20")
    if lib_path:
        cindex.Config.set_library_file(lib_path)


def main():
    header_path = sys.argv[1]
    clang_init()

    index = cindex.Index.create()
    args = [
        '-std=c99',
        '-I/usr/lib/llvm-20/lib/clang/20/include',
        '-I/usr/local/include',
        '-I/usr/include',
    ]

    tu = index.parse(header_path, args)
    for diag in tu.diagnostics:
        print(diag)
    # print_all_cursors_top_level(tu)
    # print_all_struct_definitions(tu)
    # print_all_enum_definitions(tu)
    # print_all_struct_children(tu)
    walk(tu)


main()
