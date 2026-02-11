cmake_minimum_required(VERSION 4.0)

project(baligo)

set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

if (NOT DEFINED CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 23)
endif()

if (NOT DEFINED CMAKE_C_STANDARD)
    set(CMAKE_C_STANDARD 11)
endif()

set(CMAKE_CXX_EXTENSIONS OFF)

include(cmake/PreventInSourceBuilds.cmake)
include(cmake/CPM.cmake)
include(Dependencies.cmake)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)

include(CTest)
enable_testing()

add_subdirectory(src)
add_subdirectory(test)
