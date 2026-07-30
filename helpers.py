from clang import cindex


def get_cursor_type(cursor):
    return cursor.type.get_canonical()


def get_canonical_type(cursor_or_type):
    if isinstance(cursor_or_type, cindex.Cursor):
        return cursor_or_type.type.get_canonical()
    if isinstance(cursor_or_type, cindex.Type):
        return cursor_or_type.get_canonical()
    raise TypeError(f"expected Cursor or Type, got {type(cursor_or_type)}")
