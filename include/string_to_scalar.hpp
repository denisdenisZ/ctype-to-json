#pragma once

#include <algorithm>
#include <bit>
#include <charconv>
#include <cstdint>
#include <optional>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <cctype>

#include "ctypes.hpp"

extern const std::unordered_map<std::string, ScalarKind> TypeMap;

class StringValidator {
private:
public:

    bool has_only_digits(std::string_view str) {
        if (str.empty()) {
            return false;
        }

        if (!std::all_of(str.begin(), str.end(), [](const char chr) {
            return std::isdigit(static_cast<int>(chr));
        }))
        {
            return false;
        }

        return true;
    }
};

class ScalarParser {
    friend struct ParserTestAccess;
private:
    const std::unordered_map<std::string, ScalarKind>* name_table_;
    const TypeTable* type_table_;
    StringValidator validator_{};

    bool is_power_of_two_between_8_64(std::uint32_t width);

    template<typename T>
    static std::optional<int> to_number(std::string_view str, T& out);

    template <typename T>
    static inline bool parse_and_emplace(
        std::string_view text,
        ScalarValue& out);

    std::optional<int> parse_value(
        std::string_view value,
        ScalarValue& out);

public:
    ScalarParser(
        const std::unordered_map<std::string, ScalarKind>* name_table,
        TypeTable* type_table);

    [[nodiscard]] ScalarValue parse(
        std::string_view type,
        std::uint32_t width,
        std::string_view value);

};
