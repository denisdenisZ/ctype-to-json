#include <cassert>
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string_view>

#include "string_to_scalar.hpp"
#include "ctypes.hpp"

bool ScalarParser::is_power_of_two_between_8_64(std::uint32_t width) {
    return std::has_single_bit(width) && width <= 64 && width >= 8;
}

template<typename T>
std::optional<int> ScalarParser::to_number(std::string_view str, T& out) {
    T result{};
    auto [ptr, ec] = std::from_chars(
        str.data(),
        str.data() + str.size(),
        result);

    if (!(ec == std::errc())) {
        return 1;
    }
    out = result;
    return std::nullopt;
}

template<>
std::optional<int> ScalarParser::to_number<float>(
    std::string_view str,
    float& out
) {
    float result{};
    auto [ptr, ec] = std::from_chars(
        str.data(),
        str.data() + str.size(),
        result,
        std::chars_format::general);

    if (ec != std::errc())
        return 1;

    out = result;
    return std::nullopt;
}

template <typename T>
inline bool ScalarParser::parse_and_emplace(
    std::string_view text,
    ScalarValue& out
) {
    T val{};

    if (to_number(text, val) != std::nullopt)
        return false;

    out.value.emplace<T>(val);
    return true;
}

std::optional<int> ScalarParser::parse_value(
    std::string_view value,
    ScalarValue& out)
{
    if (!validator_.has_only_digits(value)) {
        return 1;
    }

    ScalarType out_type = type_table_->scalars.at(out.kind.id);

    std::uint32_t bits = out_type.bits;
    if (!is_power_of_two_between_8_64(bits)) {
        return 1;
    }

    auto b_tag = out.to_tag(out_type);
    if (!b_tag.has_value()) {
        return 1;
    }
    switch (*b_tag) {
        case BuiltInScalarTag::U8: {
            if (!parse_and_emplace<std::uint8_t>(value, out)) {
                return 1;
            }
            break;
        }

        case BuiltInScalarTag::U16: {
            if (!parse_and_emplace<std::uint16_t>(value, out)) {
                return 1;
            }
            break;
        }

        case BuiltInScalarTag::U32: {
            if (!parse_and_emplace<std::uint32_t>(value, out)) {
                return 1;
            }
            break;
        }

        case BuiltInScalarTag::U64: {
            if (!parse_and_emplace<std::uint64_t>(value, out)) {
                return 1;
            }
            break;
        }

        case BuiltInScalarTag::I8: {
            if (!parse_and_emplace<std::int8_t>(value, out)) {
                return 1;
            }
            break;
        }

        case BuiltInScalarTag::I16: {
            if (!parse_and_emplace<std::int16_t>(value, out)) {
                return 1;
            }
            break;
        }

       case BuiltInScalarTag::I32: {
            if (!parse_and_emplace<std::int32_t>(value, out)) {
                return 1;
            }
            break;
        }

       case BuiltInScalarTag::I64: {
            if (!parse_and_emplace<std::int64_t>(value, out)) {
                return 1;
            }
            break;
        }

       case BuiltInScalarTag::F32: {
            if (!parse_and_emplace<float>(value, out)) {
                return 1;
            }
            break;
        }

    }
    return std::nullopt;
}

ScalarParser::ScalarParser(
    const std::unordered_map<std::string, ScalarKind>* name_table,
    TypeTable* type_table)
    : name_table_(name_table),
    type_table_(type_table)
{
    assert(name_table_);
    assert(type_table);
}

ScalarValue ScalarParser::parse(
    std::string_view type,
    std::uint32_t width,
    std::string_view value)
{

    ScalarValue out{};

    if (!name_table_->contains(std::string{type})) {
        throw std::invalid_argument("Type does not exist in table!");
    }

    parse_value(value, out);

    return out;
}
