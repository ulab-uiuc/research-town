#python compute_metric.py ./results_combine/main_table/research_bench_result_4o_mini_single_agent.jsonl ./results_combine/main_compute/research_bench_result_4o_mini_single_agent.jsonl

#python compute_metric.py ./results_combine/main_table/research_bench_result_4o_mini.jsonl ./results_combine/main_compute/research_bench_result_4o_mini.jsonl
python compute_metric.py ./results_combine/main_table/research_bench_result_llama3.1_72b_single_agent.jsonl ./results_combine/main_compute/research_bench_result_llama3.1_72b_single_agent.jsonl

#research_bench_result_4o.jsonl

# python ./compute_metrics.py --input_files ./results_combine/main_table/research_bench_result_4o_mini_single_agent.jsonl  --averages_dir metrics_averages

# research_bench_result_4o_mini.jsonl research_bench_result_4o_single_agent.jsonl research_bench_result_4o.jsonl research_bench_result_llama3.1_72b_single_agent.jsonl research_bench_result_llama3.1_72b.jsonl --output_dir ./results_combine/processed_outputs_main