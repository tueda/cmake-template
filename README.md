cmake-template
==============

A [CMake](https://cmake.org/) template with
[doctest](https://github.com/onqtam/doctest) and
[Google Benchmark](https://github.com/google/benchmark).


Get started
===========

1. Clone this repository.
2. Squash all the history to make an initial commit.

    ```shell
    git reset $(git commit-tree HEAD^{tree} -m "Initial commit")
    ```

3. Amend the initial commit by adding/deleting/modifying files. It may be useful
   to see results of

    ```shell
    git ls-files     # list of files in the repository
    git grep -n foo  # lines containing the dummy project name "foo"
    ```

Arguable default values you might want to look into:

- Compiler warning flags ([`CMakeLists.txt`](CMakeLists.txt))
- `ENABLE_NATIVE=ON` ([`CMakeLists.txt`](CMakeLists.txt))
- Coding conventions: Google ([`.clang-format`](.clang-format))
- Continuous integration ([`.gitlab-ci.yml`](.gitlab-ci.yml))


Build
=====

A typical CMake build process on Linux is

```shell
git submodule update --init
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/path/to/install ..
make
make check
make bench
make install
```
