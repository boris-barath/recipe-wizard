cmake_minimum_required(VERSION 3.13)
project(crawl)

set(CMAKE_CXX_STANDARD 17)

set(GCC_COVERAGE_COMPILE_FLAGS "-I/usr/local/opt/icu4c/include")
set(GCC_COVERAGE_LINK_FLAGS "-lfreeling -lboost_system -lboost_filesystem")

set(CMAKE_CXX_FLAGS_RELEASE "-O3")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${GCC_COVERAGE_COMPILE_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${GCC_COVERAGE_LINK_FLAGS}")

add_executable(crawl main.cpp config.cpp)