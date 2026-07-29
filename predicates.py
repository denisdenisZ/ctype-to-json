import clang.cindex as cindex
from helpers import get_cursor_type

NUMERIC_KINDS = (
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

ARRAY_KINDS = (
    cindex.TypeKind.CONSTANTARRAY,
    cindex.TypeKind.INCOMPLETEARRAY,
    cindex.TypeKind.VARIABLEARRAY,
)

TOP_LEVEL_RECORD_AND_ENUM_KINDS = (
    cindex.CursorKind.STRUCT_DECL,
    cindex.CursorKind.ENUM_DECL,
    cindex.CursorKind.UNION_DECL,
)


# HELPERS ===================================================================
def _resolve_if_pointer(t):
    if t.kind == cindex.TypeKind.POINTER:
        return t.get_pointee().get_canonical()
    return t


def _is_record_of_kind(cursor, decl_kind):
    t = get_cursor_type(cursor)
    return (
        t.kind == cindex.TypeKind.RECORD
        and t.get_declaration().kind == decl_kind
    )


def _has_kind(cursor, *kinds):
    return get_cursor_type(cursor).kind in kinds


def _pointee_has_kind(cursor, *kinds):
    t = _resolve_if_pointer(get_cursor_type(cursor))
    return t.kind in kinds
# ===========================================================================


def is_pointer(cursor):
    return _has_kind(cursor, cindex.TypeKind.POINTER)


def is_func_ptr(cursor):
    return _pointee_has_kind(cursor,
                             cindex.TypeKind.FUNCTIONPROTO,
                             cindex.TypeKind.FUNCTIONNOPROTO)


def is_array(cursor):
    return _has_kind(cursor, *ARRAY_KINDS)


def is_struct(cursor):
    return _is_record_of_kind(cursor, cindex.CursorKind.STRUCT_DECL)


def is_union(cursor):
    return _is_record_of_kind(cursor, cindex.CursorKind.UNION_DECL)


def is_bool(cursor):
    return _has_kind(cursor, cindex.TypeKind.BOOL)


def is_numeric(cursor):
    return _has_kind(cursor, *NUMERIC_KINDS)


def is_complex(cursor):
    return _has_kind(cursor, cindex.TypeKind.COMPLEX)


def is_enum(cursor):
    return _has_kind(cursor, cindex.TypeKind.ENUM)


def is_bitfield(cursor):
    return cursor.is_bitfield()


def is_top_level_record_or_enum_def(cursor):
    if cursor.kind not in TOP_LEVEL_RECORD_AND_ENUM_KINDS:
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
