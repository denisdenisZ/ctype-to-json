add_library(string_to_scalar
    scalar_table.cpp
    string_to_scalar.cpp
    ctypes.cpp
)

target_include_directories(string_to_scalar
    PUBLIC
        ${PROJECT_SOURCE_DIR}/include
)
