#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest.h>

#include "foo.h"

TEST_CASE("add_two") { CHECK_EQ(add_two(2, 1), 3); }

TEST_CASE("sub_two") { CHECK_EQ(sub_two(2, 1), 1); }
