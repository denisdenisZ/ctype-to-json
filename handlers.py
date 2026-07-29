from clang import cindex

from helpers import get_cursor_type


# HELPERS ===================================================================
def pointer_depth(cursor):
    depth = 0
    t = get_cursor_type(cursor)
    while t.kind == cindex.TypeKind.POINTER:
        t = t.get_pointee().get_canonical()
        depth += 1
    return depth
# ===========================================================================


def handle_top_level_struct():
    pass


def handle_top_level_enum():
    pass


def handle_top_level_union():
    pass


def handle_bitfield(cursor):
    pass


def handle_pointer(cursor):
    pass


def handle_func_ptr(cursor):
    pass


def handle_struct(cursor):
    pass


def handle_union(cursor):
    pass


def handle_enum(cursor):
    pass


def handle_bool(cursor):
    pass


def handle_array(cursor):
    pass


def handle_complex(cursor):
    pass


def handle_numeric(cursor):
    pass
