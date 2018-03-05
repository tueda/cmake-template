#include <benchmark/benchmark.h>

#include "foo.h"

static void BM_add_two(benchmark::State& state) {
  for (auto _ : state) {
    add_two(1, 2);
  }
}
BENCHMARK(BM_add_two);

static void BM_sub_two(benchmark::State& state) {
  for (auto _ : state) {
    sub_two(2, 1);
  }
}
BENCHMARK(BM_sub_two);

static void BM_vector_push_back(benchmark::State& state) {
  for (auto _ : state) {
    std::vector<int> v;
    v.reserve(1);
    benchmark::DoNotOptimize(v.data());
    v.push_back(42);
    benchmark::ClobberMemory();
  }
}
BENCHMARK(BM_vector_push_back);

BENCHMARK_MAIN()
