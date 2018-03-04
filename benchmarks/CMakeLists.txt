if(NOT CMAKE_BUILD_TYPE MATCHES Release)
  add_custom_target(bench)
  return()
endif()

include_directories(${CMAKE_SOURCE_DIR}/src)
link_libraries(foo_lib)

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
          -DCMAKE_BUILD_TYPE=Release
          -DBENCHMARK_ENABLE_TESTING=OFF
          ${CMAKE_CURRENT_SOURCE_DIR}/benchmark
  COMMAND ${CMAKE_COMMAND} --build .
  COMMAND ${CMAKE_COMMAND} -E touch ${CMAKE_CURRENT_BINARY_DIR}/stamp-h1.out
  WORKING_DIRECTORY benchmark
)

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
