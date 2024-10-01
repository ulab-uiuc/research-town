#!/bin/bash

INPUT="./benchmark/benchmark_0930.json"
OUTPUT="./results/research_bench_result.jsonl"

poetry run python run_evaluation.py --input "$INPUT" --output "$OUTPUT"
