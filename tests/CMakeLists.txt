include_directories(${CMAKE_SOURCE_DIR}/src)
link_libraries(foo_lib)

# Doctest.
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/doctest/doctest)

# Define the "check" target. Use "make check" instead of "make test"; the latter
# is known not to update executables (cmake/cmake#8774).
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure)

# Add a test.
macro(do_test testname testfile)
  add_executable(${testname}.exe ${testfile})
  add_test(${testname} ${testname}.exe --force-colors=true)
  add_dependencies(check ${testname}.exe)
endmacro()

# Add all source files starting with "test" as test programs.
file(GLOB test_list RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
     "test*.c" "test*.C" "test*.c++" "test*.cc" "test*.cpp" "test*.cxx")
foreach(testfile ${test_list})
  get_filename_component(testname ${testfile} NAME_WE)
  do_test(${testname} ${testfile})
endforeach()
