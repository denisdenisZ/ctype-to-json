import clang.cindex as clx
import json
import sys


class HeaderParser:
    def __init__(self):
        self.data = {}
        self.seen = []

    def parse(self, header: str, args: list[str]):
        index = clx.Index.create()
        return index.parse(header, args).cursor

    def get_child(self, cursor):
        return next(cursor.get_children())

    def is_from_my_file(self, cursor):
        return not cursor.location.is_in_system_header

    def is_typedef(self, cursor):
        return cursor.kind == clx.CursorKind.TYPEDEF_DECL

    def resolve_typedef(self, cursor):
        return next(cursor.get_children(), None)

    def was_seen(self, cursor):
        return cursor.hash in self.seen

    def mark_seen(self, cursor):
        self.seen.append(cursor.hash)

    def is_bool(self, cursor):
        with open(cursor.extent.start.file.name) as f:
            lines = f.readlines()
            line = lines[cursor.extent.start.line - 1]  # lines are 1-indexed
            return "bool" in line

    def process_bool(self, cursor):
        return {"type": "bool"}

    def is_ref(self, cursor):
        child = next(cursor.get_children(), None)
        if child is not None:
            decl = child.type.get_declaration()
            if self.is_from_my_file(decl):
                return True
        return False

    def process_ref(self, cursor):
        return {"ref": self.get_child(cursor).hash}

    def is_array(self, cursor):
        return cursor.type.kind == clx.TypeKind.CONSTANTARRAY

    def get_array_dimensions(self, type):
        dims = []
        while type.kind == clx.TypeKind.CONSTANTARRAY:
            dims.append(type.element_count)
            type = type.element_type
        return dims, type

    def process_array(self, cursor):
        dims, element_type = self.get_array_dimensions(cursor.type)
        result = {
            "type": element_type.spelling,
            "array": dims
        }
        decl = element_type.get_declaration()
        if decl.location.file is not None and self.is_from_my_file(decl):
            result["ref"] = decl.hash
        return result

    def is_pointer(self, cursor):
        return cursor.type.kind == clx.TypeKind.POINTER

    def process_pointer(self, cursor):
        return {"pointer": "true", "type": cursor.type.get_pointee().spelling}

    def is_unsupported(self, cursor):
        unsupported_kinds = [
            clx.TypeKind.FUNCTIONPROTO,
            clx.TypeKind.FUNCTIONNOPROTO,
        ]
        unsupported_cursor_kinds = [
            clx.CursorKind.UNION_DECL,
        ]
        return (
            cursor.type.kind in unsupported_kinds
            or cursor.is_bitfield()
            or cursor.type.get_declaration().kind in unsupported_cursor_kinds
            or cursor.type.get_declaration().is_anonymous()
        )

    def process_field(self, cursor):
        # TODO: Cases
        # fundamental arithmetic types, default assumption  V
        # is bool                                           V
        # is another user defined type from user file       V
        # is array                                          V
        # is pointer                                        V
        # is nested anonymous union/struct - make this func recursive
        # is bitfield - real pain to handle
        # is function pointer - just ignore

        if self.is_unsupported(cursor):
            loc = cursor.extent.start
            print(
                f"Unsupported field '{cursor.displayname}' "
                f"of type '{cursor.type.spelling}' "
                f"at {loc.file.name}:{loc.line}:{loc.column}"
            )
            sys.exit(1)

        field = {
                "name": cursor.displayname,
                "kind": "field",
                "type": cursor.type.spelling
        }

        if self.is_pointer(cursor):
            field |= self.process_pointer(cursor)

        if self.is_bool(cursor):
            field |= self.process_bool(cursor)
        elif self.is_array(cursor):
            field |= self.process_array(cursor)
        elif self.is_ref(cursor):
            field |= self.process_ref(cursor)

        return field

    def process_struct(self, cursor, name):
        fields = []

        self.data[cursor.hash] = {
            "name": name,
            "kind": "struct",
        }

        for child in cursor.get_children():
            fields.append(self.process_field(child))

        self.data[cursor.hash]["fields"] = fields

    def process_enum(self, cursor, name):
        self.data[cursor.hash] = {
            "name": name,
            "kind": "enum",
            "fields": [],
        }

        for child in cursor.get_children():
            self.data[cursor.hash]["fields"].append({
                "name": child.displayname,
                "type": child.type.spelling,
                "value": child.enum_value
            })

    def process_node(self, cursor, name):
        match cursor.kind:
            case clx.CursorKind.STRUCT_DECL:
                self.process_struct(cursor, name)
            case clx.CursorKind.UNION_DECL:
                pass
            case clx.CursorKind.ENUM_DECL:
                self.process_enum(cursor, name)
            case _:
                pass

        pass

    def walk(self, cursor):
        if self.is_from_my_file(cursor):
            if self.is_typedef(cursor):
                name = cursor.displayname
                child = self.resolve_typedef(cursor)
                self.data[child.hash]["name"] = name

            if not self.was_seen(cursor):
                self.process_node(cursor, cursor.type.spelling)
                self.mark_seen(cursor)

        for child in cursor.get_children():
            self.walk(child)

    def process_includes(self, cursor):
        includes = cursor.translation_unit.get_includes()
        self.data["meta"] = {
            "kind": "metadata",
            "headers": [inc.include.name for inc in includes]
        }

    def parse_header(self, header: str, args: list[str]) -> dict:

        cursor = self.parse(header, args)
        self.process_includes(cursor)
        self.walk(cursor)

        return self.data

    def parse_header_to_file(self, header: str, out: str, args: list[str]):
        self.parse_header(header, args)

        with open(out, "w") as f:
            json.dump(self.data, f, indent=2)

    def parse_headers(self, headers_dir: str):
        pass
