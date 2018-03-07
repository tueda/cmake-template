include_directories(${CMAKE_SOURCE_DIR}/src)
link_libraries(foo_lib)

# Benchmark tests should be performed in the release build.
if(NOT CMAKE_BUILD_TYPE MATCHES Release)
  add_custom_target(bench)
  return()
endif()

# Google Benchmark.
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/benchmark/include)
link_directories(${CMAKE_CURRENT_BINARY_DIR}/benchmark/src)
link_libraries(benchmark)
find_package(Threads REQUIRED)
link_libraries(${CMAKE_THREAD_LIBS_INIT})

file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/benchmark")
add_custom_command(
  OUTPUT stamp-h1.out
  COMMAND ${CMAKE_COMMAND}
          -G ${CMAKE_GENERATOR}
          -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
          -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
          -DCMAKE_BUILD_TYPE=Release
          -DBENCHMARK_ENABLE_TESTING=OFF
          ${CMAKE_CURRENT_SOURCE_DIR}/benchmark
  COMMAND ${CMAKE_COMMAND} --build .
  COMMAND ${CMAKE_COMMAND} -E touch ${CMAKE_CURRENT_BINARY_DIR}/stamp-h1.out
  WORKING_DIRECTORY benchmark
)

# Relax compiler warnings for Google Benchmark.
macro(add_cxx_compiler_flag flag)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${flag}")
endmacro()

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_cxx_compiler_flag(-Wno-covered-switch-default)
  add_cxx_compiler_flag(-Wno-global-constructors)
  add_cxx_compiler_flag(-Wno-padded)
  add_cxx_compiler_flag(-Wno-used-but-marked-unused)
  add_cxx_compiler_flag(-Wno-weak-vtables)
endif()

# Custom targets for benchmarking.
add_custom_target(bench)

# Add a bench.
macro(do_bench benchname benchfile)
  add_executable(${benchname}.exe ${benchfile} stamp-h1.out)
  add_dependencies(bench ${benchname}.exe)
  add_custom_command(TARGET bench POST_BUILD
                     COMMAND $<TARGET_FILE:${benchname}.exe>)
endmacro()

# Add all source files starting with "bench" as benchmark programs.
file(GLOB bench_list RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
     "bench*.c" "bench*.C" "bench*.c++" "bench*.cc" "bench*.cpp" "bench*.cxx")
foreach(benchfile ${bench_list})
  get_filename_component(benchname ${benchfile} NAME_WE)
  do_bench(${benchname} ${benchfile})
endforeach()
