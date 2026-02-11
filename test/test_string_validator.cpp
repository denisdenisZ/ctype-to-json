#include <catch2/catch_test_macros.hpp>

#include "string_to_scalar.hpp"

TEST_CASE("has_only_digits", "") {
    StringValidator validator{};

    SECTION("Digits only input") {
        REQUIRE(validator.has_only_digits("123"));
    }

    SECTION("Empty input") {
        REQUIRE_FALSE(validator.has_only_digits(""));
    }

    SECTION("Input with only characters") {
        REQUIRE_FALSE(validator.has_only_digits("asdf"));
    }

    SECTION("Input with digits and characters") {
        REQUIRE_FALSE(validator.has_only_digits("1asdf2sdf3"));
    }
}


