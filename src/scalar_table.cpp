#include <string>
#include <unordered_map>

#include "ctypes.hpp"
#include "string_to_scalar.hpp"

const std::unordered_map<std::string, ScalarKind> TypeMap = {

    // -------------------------------------------------
    // Plain character
    // -------------------------------------------------
    {"char", ScalarKind::Char},

    // -------------------------------------------------
    // Built-in signed integer types
    // -------------------------------------------------
    {"signed char", ScalarKind::Signed},

    {"short", ScalarKind::Signed},
    {"short int", ScalarKind::Signed},
    {"signed short", ScalarKind::Signed},
    {"signed short int", ScalarKind::Signed},

    {"int", ScalarKind::Signed},
    {"signed", ScalarKind::Signed},
    {"signed int", ScalarKind::Signed},

    {"long", ScalarKind::Signed},
    {"long int", ScalarKind::Signed},
    {"signed long", ScalarKind::Signed},
    {"signed long int", ScalarKind::Signed},

    {"long long", ScalarKind::Signed},
    {"long long int", ScalarKind::Signed},
    {"signed long long", ScalarKind::Signed},
    {"signed long long int", ScalarKind::Signed},

    // -------------------------------------------------
    // Built-in unsigned integer types
    // -------------------------------------------------
    {"unsigned char", ScalarKind::Unsigned},

    {"unsigned short", ScalarKind::Unsigned},
    {"short unsigned int", ScalarKind::Unsigned},
    {"unsigned short int", ScalarKind::Unsigned},

    {"unsigned", ScalarKind::Unsigned},
    {"unsigned int", ScalarKind::Unsigned},

    {"unsigned long", ScalarKind::Unsigned},
    {"long unsigned int", ScalarKind::Unsigned},
    {"unsigned long int", ScalarKind::Unsigned},

    {"unsigned long long", ScalarKind::Unsigned},
    {"long long unsigned int", ScalarKind::Unsigned},
    {"unsigned long long int", ScalarKind::Unsigned},

    // -------------------------------------------------
    // Fixed-width stdint types
    // -------------------------------------------------
    {"int8_t", ScalarKind::Signed},
    {"int16_t", ScalarKind::Signed},
    {"int32_t", ScalarKind::Signed},
    {"int64_t", ScalarKind::Signed},

    {"uint8_t", ScalarKind::Unsigned},
    {"uint16_t", ScalarKind::Unsigned},
    {"uint32_t", ScalarKind::Unsigned},
    {"uint64_t", ScalarKind::Unsigned},

    // -------------------------------------------------
    // Least-width stdint types
    // -------------------------------------------------
    {"int_least8_t", ScalarKind::Signed},
    {"int_least16_t", ScalarKind::Signed},
    {"int_least32_t", ScalarKind::Signed},
    {"int_least64_t", ScalarKind::Signed},

    {"uint_least8_t", ScalarKind::Unsigned},
    {"uint_least16_t", ScalarKind::Unsigned},
    {"uint_least32_t", ScalarKind::Unsigned},
    {"uint_least64_t", ScalarKind::Unsigned},

    // -------------------------------------------------
    // Fast-width stdint types
    // -------------------------------------------------
    {"int_fast8_t", ScalarKind::Signed},
    {"int_fast16_t", ScalarKind::Signed},
    {"int_fast32_t", ScalarKind::Signed},
    {"int_fast64_t", ScalarKind::Signed},

    {"uint_fast8_t", ScalarKind::Unsigned},
    {"uint_fast16_t", ScalarKind::Unsigned},
    {"uint_fast32_t", ScalarKind::Unsigned},
    {"uint_fast64_t", ScalarKind::Unsigned},
};
