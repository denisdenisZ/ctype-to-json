add_executable(unit_tests
    test_string_validator.cpp
    test_scalar_parser.cpp
)

target_link_libraries(unit_tests PRIVATE
    Catch2::Catch2WithMain
    string_to_scalar
)

target_include_directories(unit_tests
    PRIVATE
        ${PROJECT_SOURCE_DIR}/include
)

include(${Catch2_SOURCE_DIR}/extras/Catch.cmake)
catch_discover_tests(unit_tests)
