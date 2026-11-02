cmake_minimum_required(VERSION 3.20)
project(EvolutionaryPD LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include(FetchContent)
set(MATPLOTPP_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(MATPLOTPP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
FetchContent_Declare(matplotplusplus
    GIT_REPOSITORY https://github.com/alandefreitas/matplotplusplus.git
    GIT_TAG v1.2.2
    GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(matplotplusplus)
add_executable(EvolutionaryPD source/main.cpp)
target_link_libraries(EvolutionaryPD PRIVATE matplot)
