#include "ctypes.hpp"
#include <optional>

std::optional<BuiltInScalarTag> ScalarValue::to_tag(const ScalarType& scal) {
    switch (scal.kind) {
        case ScalarKind::Unsigned: {
            switch (scal.bits) {
                case 8:  return BuiltInScalarTag::U8;
                case 16: return BuiltInScalarTag::U16;
                case 32: return BuiltInScalarTag::U32;
                case 64: return BuiltInScalarTag::U64;
            }
            break;
        }

        case ScalarKind::Signed: {
            switch (scal.bits) {
                case 8:  return BuiltInScalarTag::I8;
                case 16: return BuiltInScalarTag::I16;
                case 32: return BuiltInScalarTag::I32;
                case 64: return BuiltInScalarTag::I64;
            }
            break;
        }

        case ScalarKind::Float: {
            if (scal.bits == 32) return BuiltInScalarTag::F32;
            break;
        }

        default:
            break;
    }
    return std::nullopt;
}

const ScalarType& TypeTable::get_scalar(TypeRef type) const {
    assert(type.kind == TypeKind::Scalar);
    return scalars.at(type.id);
}

const PointerType& TypeTable::get_pointer(TypeRef type) const {
    assert(type.kind == TypeKind::Pointer);
    return pointers.at(type.id);
}

const StructType& TypeTable::get_struct(TypeRef type) const {
    assert(type.kind == TypeKind::Struct);
    return structs.at(type.id);
}

const EnumType& TypeTable::get_enum(TypeRef type) const {
    assert(type.kind == TypeKind::Enum);
    return enums.at(type.id);
}

const ArrayType& TypeTable::get_array(TypeRef type) const {
    assert(type.kind == TypeKind::Array);
    return arrays.at(type.id);
}
