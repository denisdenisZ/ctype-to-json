from clang import cindex

from helpers import get_canonical_type
import hashlib

from predicates import (
    is_bool,
    is_complex,
    is_enum,
    is_numeric,
    is_struct,
    is_union,

    is_array,
    is_incomplete_array,
    is_vla_array,

    is_pointer,
    is_func_ptr,
    is_bitfield,

    is_numeric_signed,
    is_numeric_float,
)


# HELPERS ===================================================================
def _bytes_to_bits(num):
    return num * 8


def _dispatch(cursor, dispatch_list):
    for predicate, handler in dispatch_list:
        if predicate(cursor):
            return handler(cursor)
    # FIXME: Return better error
    return False


def _pointer_depth(cursor):
    depth = 0
    t = get_canonical_type(cursor)
    while t.kind == cindex.TypeKind.POINTER:
        t = t.get_pointee().get_canonical()
        depth += 1
    return depth


def _get_underlying_enum_const_type(cursor):
    return cursor.type.get_canonical().spelling


def _get_underlying_enum_type(cursor):
    return _get_underlying_enum_const_type(next(cursor.get_children(), None))


KIND_MAP_TABLE = [
    (is_func_ptr,   "func_pointer"),
    (is_pointer,    "pointer"),
    (is_array,      "array"),
    (is_bool,       "bool"),
    (is_enum,       "enum"),
    (is_struct,     "struct"),
    (is_union,      "union"),
    (is_complex,    "complex"),
    (is_numeric,    "numeric"),
]


def _get_struct_field_kind(cursor):
    for predicate, name in KIND_MAP_TABLE:
        if predicate(cursor):
            return name


def _stable_id(s: str, length: int = 12) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:length]


def _gen_anon_name(s: str) -> str:
    base = "__anon_"
    return base + _stable_id(s, 12)


def _gen_type_name(cursor_or_type):
    typ = get_canonical_type(cursor_or_type)
    cur = typ.get_declaration()

    if not cur.is_anonymous():
        return typ.spelling
    parts = [
        f"{field.spelling}:{get_canonical_type(field).spelling}"
        for field in cur.get_children()
    ]
    type_decl = cur.kind.name
    name = f"{type_decl}:" + "_".join(parts)
    return _gen_anon_name(name)


def _get_size_bits(cursor):
    return _bytes_to_bits(get_canonical_type(cursor).get_size())


def _resolve_decl(cursor):
    return get_canonical_type(cursor).get_declaration()


def _get_pointee_ref(cursor):
    c_type = get_canonical_type(cursor)
    pointee = c_type.get_pointee().get_canonical()

    if pointee.kind == cindex.TypeKind.RECORD:
        decl = pointee.get_declaration()
        return _gen_type_name(decl)

    return pointee.spelling


def _get_underlying_pointer_type_name(cursor_or_type):
    t = get_canonical_type(cursor_or_type)
    if not is_pointer(t):
        return _gen_type_name(t)
    return _get_underlying_pointer_type_name(t.get_pointee())


def _get_underlying_array_type_name(cursor_or_type):
    t = get_canonical_type(cursor_or_type)
    if not is_array(t):
        return _gen_type_name(t)
    return _get_underlying_pointer_type_name(t.get_array_element_type())


def _unroll_pointer(cursor_or_type, out=None, depth=1):
    cursor_or_type = get_canonical_type(cursor_or_type)
    if out is None:
        out = {}

    if not is_pointer(cursor_or_type):
        base_entries = dispatch_field(cursor_or_type)
        if base_entries:
            out.update(base_entries)
        return out

    _unroll_pointer(cursor_or_type.get_pointee(), out, depth+1)
    ref = _get_underlying_pointer_type_name(cursor_or_type)
    name = ref + "*"*depth
    out[name] = {
        "kind": "pointer",
        "ref": ref,
    }
    return out


def _unroll_array(cursor_or_type, out=None):
    cursor_or_type = get_canonical_type(cursor_or_type)
    if out is None:
        out = {}

    if not is_array(cursor_or_type):
        base_entries = dispatch_field(cursor_or_type)
        if base_entries:
            out.update(base_entries)
        return out

    _unroll_array(cursor_or_type.get_array_element_type(), out)
    ref = _get_underlying_array_type_name(cursor_or_type)
    size = cursor_or_type.get_array_size()
    name = f"{ref}[{size}]"
    out[name] = {
        "kind": "array",
        "ref": ref,
        "size": size,
        "incomplete": True if is_incomplete_array(cursor_or_type) else False,
        "vla": True if is_vla_array(cursor_or_type) else False,

        "size_bits": _get_size_bits(cursor_or_type),
        "align_bytes": cursor_or_type.get_align(),
    }
    return out
# ===========================================================================


def _handle_top_level_record(cursor, kind):
    out = {}
    c_type = get_canonical_type(cursor)
    name = _gen_type_name(cursor)
    out[name] = {
        "kind": kind,
        "c_type": c_type.spelling,
        "size_bits": _get_size_bits(cursor),
        "align_bytes": c_type.get_align(),
        "fields": [],
    }
    for field in cursor.get_children():
        out[name]["fields"].append(
            {
                "name": field.spelling,
                "kind": _get_struct_field_kind(field),
                "offset_bits": c_type.get_offset(field.spelling),
                "ref": _gen_type_name(field),
                "is_bitfield": True if is_bitfield(field) else False,
                "width": (
                    field.get_bitfield_width()
                    if is_bitfield(field)
                    else None
                ),
            }
        )
    return out


def handle_top_level_struct(cursor):
    return _handle_top_level_record(cursor, "struct")


def handle_top_level_union(cursor):
    return _handle_top_level_record(cursor, "union")


def handle_top_level_enum(cursor):
    out = {}
    name = _gen_type_name(cursor)
    out[name] = {
        "kind": "enum",
        "c_type": get_canonical_type(cursor).spelling,
        "underlying_type": _get_underlying_enum_type(cursor),

        "fields": [],
    }

    for field in cursor.get_children():
        out[name]["fields"].append(
            {
                "name": field.spelling,
                "kind": "enum_const",
                "ref": get_canonical_type(field).spelling,
                "value": field.enum_value,
            }
        )

    return out


def handle_pointer_field(cursor):
    return _unroll_pointer(cursor)


def handle_func_ptr_field(cursor):
    out = {}
    out[_gen_type_name(cursor)] = {
        "kind": "func_pointer"
    }
    return out


def handle_struct_field(cursor):
    return _handle_top_level_record(_resolve_decl(cursor), "struct")


def handle_union_field(cursor):
    return _handle_top_level_record(_resolve_decl(cursor), "union")


def handle_enum_field(cursor):
    return handle_top_level_enum(_resolve_decl(cursor))


def handle_bool_field(cursor):
    out = {}
    c_type = get_canonical_type(cursor)
    out[_gen_type_name(cursor)] = {
        "kind": "bool",

        "size_bits": _get_size_bits(cursor),
        "align_bytes": c_type.get_align(),
    }
    return out


def handle_array_field(cursor):
    return _unroll_array(cursor)


def handle_complex_field(cursor):
    out = {}
    c_type = get_canonical_type(cursor)
    out[_gen_type_name(cursor)] = {
        "kind": "complex",

        "size_bits": _get_size_bits(cursor),
        "align_bits": c_type.get_align(),
    }
    return out


def handle_numeric_field(cursor):
    out = {}
    c_type = get_canonical_type(cursor)
    out[_gen_type_name(cursor)] = {
        "kind": "numeric",

        "size_bits": _get_size_bits(cursor),
        "align_bytes": c_type.get_align(),

        "is_signed": is_numeric_signed(cursor),
        "is_float": is_numeric_float(cursor),

    }
    return out


FIELD_DISPATCH = [
    (is_pointer,  handle_pointer_field),
    (is_func_ptr, handle_func_ptr_field),
    (is_array,    handle_array_field),
    (is_bool,     handle_bool_field),
    (is_enum,     handle_enum_field),
    (is_struct,   handle_struct_field),
    (is_union,    handle_union_field),
    (is_complex,  handle_complex_field),
    (is_numeric,  handle_numeric_field),
]

TOP_LEVEL_DISPATCH = [
    (is_struct, handle_top_level_struct),
    (is_enum, handle_top_level_enum),
    (is_union, handle_top_level_union),
]


def dispatch_top_level(cursor):
    out = _dispatch(cursor, TOP_LEVEL_DISPATCH)
    # FIXME: Return better error
    return out if out else False


def dispatch_field(field):
    out = _dispatch(field, FIELD_DISPATCH)
    # FIXME: Return better error
    return out if out else False
