include(cmake/CPM.cmake)

cpmaddpackage(
    NAME tinyxml2
    GITHUB_REPOSITORY leethomason/tinyxml2
    GIT_TAG 11.0.0
)

cpmaddpackage(
    NAME catch2
    GITHUB_REPOSITORY catchorg/Catch2
    VERSION 3.12.0
)
