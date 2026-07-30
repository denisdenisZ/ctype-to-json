import clang.cindex as cindex
from helpers import get_canonical_type

SIGNED_NUMERIC_KINDS = (
    cindex.TypeKind.CHAR_S,
    cindex.TypeKind.SCHAR,
    cindex.TypeKind.SHORT,
    cindex.TypeKind.INT,
    cindex.TypeKind.LONG,
    cindex.TypeKind.LONGLONG,
)

FLOAT_NUMERIC_KINDS = (
    cindex.TypeKind.FLOAT,
    cindex.TypeKind.DOUBLE,
    cindex.TypeKind.LONGDOUBLE,
)

UNSIGNED_NUMERIC_KINDS = (
    cindex.TypeKind.CHAR_U,
    cindex.TypeKind.UCHAR,

    cindex.TypeKind.USHORT,

    cindex.TypeKind.UINT,

    cindex.TypeKind.ULONG,
    cindex.TypeKind.ULONGLONG,
)

NUMERIC_KINDS = (
    SIGNED_NUMERIC_KINDS + UNSIGNED_NUMERIC_KINDS + FLOAT_NUMERIC_KINDS
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
    t = get_canonical_type(cursor)
    return (
        t.kind == cindex.TypeKind.RECORD
        and t.get_declaration().kind == decl_kind
    )


def _has_type_kind(cursor_or_type, *kinds):
    return get_canonical_type(cursor_or_type).kind in kinds


def _has_kind(cursor, *kinds):
    return cursor.kind in kinds


def _pointee_has_kind(cursor, *kinds):
    t = _resolve_if_pointer(get_canonical_type(cursor))
    return t.kind in kinds
# ===========================================================================


def is_pointer(cursor):
    is_ptr_type = _has_type_kind(cursor, cindex.TypeKind.POINTER)
    return is_ptr_type and not is_func_ptr(cursor)


def is_func_ptr(cursor):
    return _pointee_has_kind(cursor,
                             cindex.TypeKind.FUNCTIONPROTO,
                             cindex.TypeKind.FUNCTIONNOPROTO)


def is_array(cursor):
    return _has_type_kind(cursor, *ARRAY_KINDS)


def is_incomplete_array(cursor):
    return _has_type_kind(cursor, cindex.TypeKind.INCOMPLETEARRAY)


def is_vla_array(cursor):
    return _has_type_kind(cursor, cindex.TypeKind.VARIABLEARRAY)


def is_struct(cursor):
    return _is_record_of_kind(cursor, cindex.CursorKind.STRUCT_DECL)


def is_union(cursor):
    return _is_record_of_kind(cursor, cindex.CursorKind.UNION_DECL)


def is_bool(cursor):
    return _has_type_kind(cursor, cindex.TypeKind.BOOL)


def is_numeric(cursor):
    return _has_type_kind(cursor, *NUMERIC_KINDS)


def is_complex(cursor):
    return _has_type_kind(cursor, cindex.TypeKind.COMPLEX)


def is_enum(cursor):
    return _has_type_kind(cursor, cindex.TypeKind.ENUM)


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


def is_numeric_signed(cursor):
    kind = get_canonical_type(cursor).kind
    if kind in SIGNED_NUMERIC_KINDS:
        return True
    if kind in UNSIGNED_NUMERIC_KINDS:
        return False
    return None


def is_numeric_float(cursor):
    return get_canonical_type(cursor).kind in FLOAT_NUMERIC_KINDS
