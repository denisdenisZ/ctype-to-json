#pragma once

#include <cassert>
#include <cstdint>
#include <optional>
#include <string>
#include <unordered_map>
#include <variant>
#include <vector>

enum class ScalarKind { Signed, Unsigned, Float, Bool, Char };
enum class BuiltInScalarTag { U8, I8, U16, I16, U32, I32, U64, I64, F32 };
enum class PtrKind { Object, Function };
enum class TypeKind { Struct, Enum, Scalar, Pointer, Array };

struct TypeRef {
    std::uint32_t id;
    TypeKind kind;
};

struct ScalarType {
    ScalarKind kind;
    BuiltInScalarTag tag;

    std::uint32_t bits;
};

struct PointerType {
    PtrKind kind;
    TypeRef pointee;
};

struct FieldDef {
    TypeRef type;
    std::string name;
};

struct StructType {
    std::string name;
    std::vector<FieldDef> fields;
};

struct Enumerator {
    std::string name;
    std::uint64_t bits;
};

struct EnumType {
    TypeRef underlying; // NOTE: Must be scalar

    std::string name;
    std::vector<Enumerator> enumerators;
};

struct ArrayType {
    TypeRef element;
    std::optional<std::uint32_t> count;
};

using ScalarValueType = std::variant<
    std::uint8_t, std::int8_t,
    std::uint16_t, std::int16_t,
    std::uint32_t, std::int32_t,
    std::uint64_t, std::int64_t,
    float >;
struct ScalarValue {
    TypeRef kind;
    ScalarValueType value;

    std::optional<BuiltInScalarTag> to_tag(const ScalarType& scal);

    // NOTE: too ambitious, maybe someday
    // std::vector<std::byte> bytes;
};

struct TypeTable {
    std::unordered_map<std::uint32_t, ScalarType>  scalars;
    std::unordered_map<std::uint32_t, PointerType> pointers;
    std::unordered_map<std::uint32_t, StructType>  structs;
    std::unordered_map<std::uint32_t, EnumType>    enums;
    std::unordered_map<std::uint32_t, ArrayType>   arrays;

    const ScalarType& get_scalar(TypeRef type) const;
    const PointerType& get_pointer(TypeRef type) const;
    const StructType& get_struct(TypeRef type) const;
    const EnumType& get_enum(TypeRef type) const;
    const ArrayType& get_array(TypeRef type) const;
};

