# Evaluating OpenHands-Versa on SWE-Bench Multimodal

This folder contains the evaluation harness for SWE-Bench Multimodal benchmark. It is built on top of the original [SWE-Bench benchmark](https://www.swebench.com/) ([paper](https://arxiv.org/abs/2310.06770)).

The evaluation consists of three steps:

1. Environment setup: [install python environment and configure LLM config](../../../README.md#installation). Make sure you have an API Key to Tavily Search API.
2. [Run inference](#run-inference-on-swe-bench-instances): Generate an edit patch for each Github issue
3. [Evaluate patches using sb-cli](#evaluate-generated-patches)

## Setup Environment and LLM Configuration

Please follow instruction [here](../../../README.md#installation) to setup your local development environment and LLM.

## Run Inference on SWE-Bench Multimodal Instances: Generate Patch from Problem Statement

> [!NOTE]
> **Iterative Evaluation Protocol**
>
> We use an iterative approach for more stable and reproducible results:
> - For each instance, we attempt to generate a solution up to 3 times
> - Each attempt continues until either:
>   1. The agent successfully produces a patch with `AgentFinishAction`, or
>   2. The attempt reaches the maximum iteration limit
> - If an attempt fails, we retry with a fresh attempt (up to the 3-attempt maximum)
> - If your LLM config has temperature=0, we will automatically use temperature=0.1 for the 2nd and 3rd attempts
> To reproduce our results, you must enable this iterative protocol and set `export ITERATIVE_EVAL_MODE=true`

### Running in parallel with RemoteRuntime

To speed up our evaluation process and run OpenHands-Versa in the cloud, we use the [OpenHands Remote Runtime](https://www.all-hands.dev/blog/evaluation-of-llms-as-coding-agents-on-swe-bench-at-30x-speed), which is currently in beta (read [here](https://runtime.all-hands.dev/) for more details). This ensures that you don't need a powerful machine to run evaluation.

To use Remote Runtime, you must fill out [this form](https://docs.google.com/forms/d/e/1FAIpQLSckVz_JFwg2_mOxNZjCtr7aoBFI2Mwdan3f75J_TrdMS1JV2g/viewform) to apply for a Remote Runtime API Key!

To run OpenHands-Versa on SWE-Bench Multimodal, run the following commands from the root directory of this repository:

```bash
export SEARCH_API_KEY=<TAVILY SEARCH API KEY>
export ITERATIVE_EVAL_MODE=true
POETRY_BIN=$(which poetry) ALLHANDS_API_KEY="YOUR-API-KEY" RUNTIME=remote SANDBOX_REMOTE_RUNTIME_API_URL="https://runtime.eval.all-hands.dev" sudo -E bash evaluation/benchmarks/swe_bench/scripts/run_infer.sh [llm-config] [git-version] [agent-name] [eval_limit] [max_iter] [num_workers] [dataset-name] [dataset_split]
```
where
- `llm-config` is the config group name for your LLM settings, as defined in your `config.toml` , e.g. `llm.claude_3_7`
- `git-version` is the git commit hash of the OpenHands-Versa version you would
like to evaluate, e.g. `HEAD`
- `agent` is the name of the agent for benchmarks, defaulting
to `CodeActAgent`. OpenHands-Versa uses `CodeActAgent` for all its experiments.
- `eval_limit`, e.g. `10`, limits the evaluation to the first `eval_limit` instances. Note: in order to use `eval_limit`, you must also set `agent`.
- `max_iter`, e.g. `20`, is the maximum number of iterations for the agent to run. By
default, it is set to 100.
- `num_workers`, e.g. `3`, is the number of parallel workers to run the evaluation. By
default, it is set to 1.
- `dataset`, a huggingface dataset name. e.g. `princeton-nlp/SWE-bench`, `princeton-nlp/SWE-bench_Lite`, `princeton-nlp/SWE-bench_Verified`, or `princeton-nlp/SWE-bench_Multimodal`, specifies which dataset to evaluate on.
- `dataset_split`, split for the huggingface dataset. e.g., `test`, `dev`. Default to `test`.

Optionally, you can set the environment variable `DEFAULT_RUNTIME_RESOURCE_FACTOR` to a higher value (like 2,4 or 8 - only multiples of 2 are allowed) instead of 1 (the default value) to use more CPU cores during inference and reduce the occurrence of runtime crashes. We set `DEFAULT_RUNTIME_RESOURCE_FACTOR` to 2 for our evaluation. Note that using a higher value of `DEFAULT_RUNTIME_RESOURCE_FACTOR` costs more API credits in the Remote Runtime API.

Given below is an example to run OpenHands-Versa on SWE-Bench Multimodal test set. You can configure the llm-config as required, and all other configuration parameters below are the ones used in our paper. This command runs evaluation on CodeActAgent (the default agent for OpenHands-Versa) for 517 instances on "princeton-nlp/SWE-bench_Multimodal"'s test set, with max 100 iteration per instances, with 16 workers running in parallel in the remote runtime.
```bash
POETRY_BIN=$(which poetry) ALLHANDS_API_KEY="YOUR-API-KEY" RUNTIME=remote SANDBOX_REMOTE_RUNTIME_API_URL="https://runtime.eval.all-hands.dev" sudo -E bash evaluation/benchmarks/swe_bench/scripts/run_infer.sh llm.claude4 HEAD CodeActAgent 517 100 16 "princeton-nlp/SWE-bench_Multimodal" test
```

To clean-up all existing runtime you've already started, run:

```bash
ALLHANDS_API_KEY="YOUR-API-KEY" bash evaluation/utils/scripts/cleanup_remote_runtime.sh
```

### Running Locally with Docker

Make sure your Docker daemon is running, and you have ample disk space (at least 200-500GB - these estimates are approximate, we have never run OpenHands-Versa on the full test split locally) for the instance-level docker image.

When the `run_infer.sh` script is started, it will automatically pull the relevant SWE-Bench images.
For example, for instance ID `django_django-11011`, it will try to pull our pre-build docker image `sweb.eval.x86_64.django_s_django-11011` from DockerHub.
This image will be used create an OpenHands runtime image where the agent will operate on.

To run OpenHands-Versa on SWE-Bench Multimodal locally with docker, run the following commands:
```bash
export SEARCH_API_KEY=<TAVILY SEARCH API KEY>
export ITERATIVE_EVAL_MODE=true
POETRY_BIN=$(which poetry) sudo -E bash evaluation/benchmarks/swe_bench/scripts/run_infer.sh [llm-config] [git-version] [agent-name] [eval_limit] [max_iter] [num_workers] [dataset-name] [dataset_split]
```
where the configuration parameters are explained [here](#running-in-parallel-with-remoteruntime)

Given below is an example to run OpenHands-Versa on SWE-Bench Multimodal test set. You can configure the llm-config as required. This command runs evaluation on CodeActAgent (the default agent for OpenHands-Versa) for 517 instances on "princeton-nlp/SWE-bench_Multimodal"'s test set, with max 100 iteration per instances, with 1 worker running locally on your machine inside a docker container.

```bash
POETRY_BIN=$(which poetry) sudo -E bash evaluation/benchmarks/swe_bench/scripts/run_infer.sh llm.claude4 HEAD CodeActAgent 517 100 1 "princeton-nlp/SWE-bench_Multimodal" test
```

> [!CAUTION]
> Setting `num_workers` larger than 1 is not officially tested, YMMV.

### Specify a subset of tasks to run infer

If you would like to specify a list of tasks you'd like to benchmark on, you could
create a `config.toml` under `./evaluation/benchmarks/swe_bench/` folder, and put a list
attribute named `selected_ids`, e.g.

```toml
selected_ids = ['sphinx-doc__sphinx-8721', 'sympy__sympy-14774', 'scikit-learn__scikit-learn-10508']
```

Then only these tasks (rows whose `instance_id` is in the above list) will be evaluated.
In this case, `eval_limit` option applies to tasks that are in the `selected_ids` list.

## Evaluate Generated Patches

After running the inference, you will obtain a `output.jsonl` (by default it will be saved to a subdirectory inside `evaluation/evaluation_outputs`, for eg: `evaluation/evaluation_outputs/outputs/princeton-nlp__SWE-bench_Multimodal-test/CodeActAgent/claude-sonnet-4-20250514_maxiter_100_N_v0.28.1-no-hint-run_1/`). We must use `sb-cli` to evaluate the generated patches and it requires the output to follow a specific format. Run the below command to process the output.jsonl file into the desired format:

```bash
python evaluation/benchmarks/swe_bench/sb_cli_translate.py --input_file <path to output.jsonl file> --output_file <path where you would like to store the processed json file> --model_name <name of the llm used for evaluation>
```

For example:
```bash
python evaluation/benchmarks/swe_bench/sb_cli_translate.py --input_file ./evaluation/evaluation_outputs/outputs/princeton-nlp__SWE-bench_Multimodal-test/CodeActAgent/claude-sonnet-4-20250514_maxiter_100_N_v0.28.1-no-hint-run_1/output.jsonl --output_file ./output_sb_cli.json --model_name "claude-sonnet-4"
```

To use sb-cli to evaluate the generated patches on SWE-Bench Multimodal, you must generate an API key using the instructions given on the [website](https://www.swebench.com/sb-cli/). After setting up sb-cli, you should run the following commands to evaluate the generated patches:

```bash
pip install sb-cli ## you must have already run this to get the sb-cli API key
export SWEBENCH_API_KEY=<your_sb_cli_api_key>
sb-cli submit swe-bench-m test --predictions_path <path to the output json file used in sb_cli_translate.py> --run_id your-run-id ## you can choose any run-id, make sure you save it somewhere in case you want to submit to the leaderboard
```

The above command will generate an evaluation report and save results in the same directory as as that of the `predictions_path`. For more details about evaluating patches using sb-cli, submissions to leaderboard, and other configuration options, please refer to this [webpage](https://www.swebench.com/sb-cli/submit-to-leaderboard/).
