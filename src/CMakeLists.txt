set(LIB_SOURCES
  foo.cpp
)

set (BIN_SOURCES
  ${LIB_SOURCES}
  main.cpp
)

add_executable(foo.exe ${BIN_SOURCES})
add_library(foo_lib STATIC EXCLUDE_FROM_ALL ${LIB_SOURCES})
