#include <iostream>
#include "foo.h"

int main() {
  std::cout << "Hello World!" << std::endl;
  std::cout << "1 + 2 = " << add_two(1, 2) << std::endl;
  std::cout << "2 - 1 = " << sub_two(2, 1) << std::endl;
}
