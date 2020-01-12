cmake_minimum_required(VERSION 3.15)

project(cpp-fviz-tests)
find_package(GTest REQUIRED)

add_compile_options(-Wall -Wextra -std=c++17)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED on)

include_directories(
    ../include
    ${GTEST_INCLUDE_DIRS}
)

set (PROJECT_SOURCES ../src)

add_executable(tests ./main.cpp ../src/sysgroup.cpp)

target_link_libraries(tests ${GTEST_LIBRARIES})

enable_testing()