cmake_minimum_required(VERSION 3.0)

project(foo VERSION 0.1.0)

# Enable C++11.
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(src)
