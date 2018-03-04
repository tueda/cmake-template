cmake_minimum_required(VERSION 3.0)

project(foo VERSION 0.1.0)

# Enable C++11.
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable tests.
enable_testing()
# Use "make check" instead of "make test"; the latter is known not to update
# executables (cmake/cmake#8774).
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure)

add_subdirectory(src)
add_subdirectory(tests EXCLUDE_FROM_ALL)
