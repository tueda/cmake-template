cmake_minimum_required(VERSION 3.0)

project(foo VERSION 0.1.0)

# Enable C++11.
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Macros for compiler flags.
include(CheckCXXCompilerFlag)

macro(add_cxx_compiler_flag flag)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${flag}")
endmacro()

macro(try_cxx_compiler_flag flag var)
  check_cxx_compiler_flag(${flag} ${var})
  if(${var})
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${flag}")
  endif()
endmacro()

# Warning flags.
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
  add_cxx_compiler_flag(-Wall)
  add_cxx_compiler_flag(-Wextra)
  add_cxx_compiler_flag(-pedantic)

# add_cxx_compiler_flag(-Waggregate-return)
  add_cxx_compiler_flag(-Wcast-align)
  add_cxx_compiler_flag(-Wcast-qual)
  add_cxx_compiler_flag(-Wconversion)
  add_cxx_compiler_flag(-Wctor-dtor-privacy)
  add_cxx_compiler_flag(-Wdisabled-optimization)
# add_cxx_compiler_flag(-Weffc++)
  add_cxx_compiler_flag(-Wfloat-equal)
  add_cxx_compiler_flag(-Wformat=2)
# add_cxx_compiler_flag(-Winline)
  add_cxx_compiler_flag(-Winvalid-pch)
  add_cxx_compiler_flag(-Wlogical-op)
  add_cxx_compiler_flag(-Wmissing-include-dirs)
  add_cxx_compiler_flag(-Wmissing-declarations)
  add_cxx_compiler_flag(-Wnon-virtual-dtor)
  add_cxx_compiler_flag(-Wold-style-cast)
  add_cxx_compiler_flag(-Woverloaded-virtual)
  add_cxx_compiler_flag(-Wpointer-arith)
  add_cxx_compiler_flag(-Wredundant-decls)
  add_cxx_compiler_flag(-Wshadow)
  add_cxx_compiler_flag(-Wsign-conversion)
# add_cxx_compiler_flag(-Wstrict-overflow=5)
  add_cxx_compiler_flag(-Wswitch-default)
  add_cxx_compiler_flag(-Wswitch-enum)
  add_cxx_compiler_flag(-Wundef)
  add_cxx_compiler_flag(-Wwrite-strings)

  if(NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS 4.6)
    add_cxx_compiler_flag(-Wnoexcept)
  endif()

  if(NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS 5.0)
    add_cxx_compiler_flag(-Wdouble-promotion)
    add_cxx_compiler_flag(-Wtrampolines)
    add_cxx_compiler_flag(-Wuseless-cast)
    add_cxx_compiler_flag(-Wvector-operation-performance)
    add_cxx_compiler_flag(-Wzero-as-null-pointer-constant)
  endif()

  if(NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS 6.0)
    add_cxx_compiler_flag(-Wshift-overflow=2)
    add_cxx_compiler_flag(-Wnull-dereference)
    add_cxx_compiler_flag(-Wduplicated-cond)
  endif()

  if(NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS 7.0)
    add_cxx_compiler_flag(-Walloc-zero)
    add_cxx_compiler_flag(-Walloca)
    add_cxx_compiler_flag(-Wduplicated-branches)
    add_cxx_compiler_flag(-Wrestrict)
  endif()
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_cxx_compiler_flag(-Weverything)
  add_cxx_compiler_flag(-Wno-c++98-compat-pedantic)
  add_cxx_compiler_flag(-pedantic)
endif()

# Strict mode.
option(ENABLE_STRICT "Turn compiler warnings into errors." OFF)
if(ENABLE_STRICT)
  try_cxx_compiler_flag("-Werror" CXX_HAS_ERROR_FLAG)
  if(NOT CXX_HAS_ERROR_FLAG)
    message(FATAL_ERROR "-Werror option not available")
  endif()
  try_cxx_compiler_flag("-pedantic-errors" CXX_HAS_PEDANTIC_ERRORS_FLAG)
  if(NOT CXX_HAS_PEDANTIC_ERRORS_FLAG)
    message(FATAL_ERROR "-pedantic-errors option not available")
  endif()
endif()

# Native option.
option(ENABLE_NATIVE "Use inative instruction sets on the build machine." ON)
if(ENABLE_NATIVE)
  try_cxx_compiler_flag("-march=native" CXX_HAS_NATIVE_FLAG)
  if(NOT CXX_HAS_NATIVE_FLAG)
    message(FATAL_ERROR "-march=native option not available")
  endif()
endif()

# Sanitizer.
option(ENABLE_SANITIZER "Build with sanitizer." OFF)
if(ENABLE_SANITIZER)
  # NOTE: -fno-sanitize-recover=all is needed to make test programs return
  # non-zero exit code for undefined behaviours.
  set(CMAKE_REQUIRED_FLAGS
      "-fsanitize=address,undefined -fno-sanitize-recover=all")
  try_cxx_compiler_flag("-fsanitize=address,undefined -fno-sanitize-recover=all"
                        CXX_HAS_SANITIZE_FLAG)
  unset(CMAKE_REQUIRED_FLAGS)

  if(NOT CXX_HAS_SANITIZE_FLAG)
    # GCC on Trusty needs explicit -fuse-ld=gold.
    # https://stackoverflow.com/a/42141358/9105334
    set(CMAKE_REQUIRED_FLAGS
        "-fsanitize=address,undefined -fno-sanitize-recover=all -fuse-ld=gold")
    try_cxx_compiler_flag(
      "-fsanitize=address,undefined -fno-sanitize-recover=all"
      CXX_HAS_SANITIZE_FLAG_TRUSTY_WORKAROUND)
    unset(CMAKE_REQUIRED_FLAGS)

    if(NOT CXX_HAS_SANITIZE_FLAG_TRUSTY_WORKAROUND)
      message(FATAL_ERROR "sanitizer option not available")
    endif()

    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fuse-ld=gold")
  endif()
endif()

# Debugging flags.
if(CMAKE_BUILD_TYPE MATCHES Debug)
  try_cxx_compiler_flag("-Og" CXX_HAS_OPTDEBUG_FLAG)
endif()

# Enable tests.
enable_testing()

add_subdirectory(src)
add_subdirectory(tests EXCLUDE_FROM_ALL)
add_subdirectory(benchmarks EXCLUDE_FROM_ALL)
