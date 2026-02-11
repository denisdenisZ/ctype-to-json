#include "catch2/catch_test_macros.hpp"
#include "string_to_scalar.hpp"
#include <cstdint>
#include <optional>

struct ParserTestAccess {
    template <typename T>
    static std::optional<int> to_number(ScalarParser& parser, std::string_view str, T& out) {
        return parser.to_number(str, out);
    }
};

TEST_CASE("to_number", "") {
    SECTION("Valid unsigned input") {
        ScalarParser sparser{&TypeMap};
        std::uint64_t num = 0;
        std::optional<int> res = ParserTestAccess::to_number(
            sparser,
            "123",
            num);
        REQUIRE(res == std::nullopt);
        REQUIRE(num == 123);
    }

    SECTION("Valid negative input") {
        ScalarParser sparser{&TypeMap};
        int num = 0;
        std::optional<int> res = ParserTestAccess::to_number(
            sparser,
            "-123",
            num);
        REQUIRE(res == std::nullopt);
        REQUIRE(num == -123);
    }

    SECTION("Input too large for type") {
        ScalarParser sparser{&TypeMap};
        std::uint8_t num = 0;
        std::optional<int> res = ParserTestAccess::to_number(
            sparser,
            "256",
            num);
        REQUIRE(res != std::nullopt);
        REQUIRE(num == 0);
    }

    SECTION("Input has no digits") {
        ScalarParser sparser{&TypeMap};
        std::uint8_t num = 0;
        std::optional<int> res = ParserTestAccess::to_number(
            sparser,
            "aaa",
            num);
        REQUIRE(res != std::nullopt);
        REQUIRE(num == 0);
    }
}
