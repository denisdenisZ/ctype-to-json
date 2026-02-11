
find_program(RUN_CLANG_TIDY run-clang-tidy)
find_program(CLANG_TIDY clang-tidy)

if (RUN_CLANG_TIDY AND CLANG_TIDY)
    add_custom_target(clang-tidy
        COMMAND ${RUN_CLANG_TIDY}
    )
endif()

macro(myproject_enable_include_what_you_use)
    find_program(INCLUDE_WHAT_YOU_USE include-what-you-use)
    if(INCLUDE_WHAT_YOU_USE)
    set(CMAKE_CXX_INCLUDE_WHAT_YOU_USE ${INCLUDE_WHAT_YOU_USE})
else()
    message(${WARNING_MESSAGE} "include-what-you-use requested but executable not found")
    endif()
endmacro()

