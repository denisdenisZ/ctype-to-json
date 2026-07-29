import clang.cindex as cindex


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
    if cursor.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
        print("enum value:    ", cursor.enum_value)
    print("is_bitfield:   ", cursor.is_bitfield())
    if cursor.is_bitfield():
        print("bitfield_width:", cursor.get_bitfield_width())
    print("semantic parent:",
          cursor.semantic_parent.spelling if cursor.semantic_parent else None)
    print("lexical parent: ",
          cursor.lexical_parent.spelling if cursor.lexical_parent else None)
    print("hash:          ", cursor.hash)
    print("USR:           ", cursor.get_usr())
    print()
    print()
