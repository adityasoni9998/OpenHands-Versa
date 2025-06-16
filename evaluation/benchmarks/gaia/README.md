# Evaluating OpenHands-Versa on GAIA

This folder contains evaluation harness for evaluating OpenHands-Versa on the [GAIA benchmark](https://arxiv.org/abs/2311.12983).

The evaluation consists of three steps:

1. Environment setup: [install python environment and configure LLM config](../../../README.md#installation). Make sure you have an API Key to Tavily Search API.
2. [Run Evaluation](#run-inference-on-gaia): Run inference on all tasks and re-run failed tasks if any.
3. [Post-processing results](#extract-and-reformat-answer)

## Setup Environment and LLM Configuration

Please follow instruction [here](../../../README.md#installation) to setup your local development environment and LLM.

## Run Inference on GAIA

We are using the GAIA dataset hosted on [Hugging Face](https://huggingface.co/datasets/gaia-benchmark/GAIA).
Please accept the terms and make sure to have logged in on your computer by `huggingface-cli login` before running the evaluation. You will need to install `huggingface-cli` using the command `pip install -U "huggingface_hub[cli]"`.

Run the following steps to start your evaluation (activate your conda environment before running these commands):

```bash
export SEARCH_API_KEY="<YOUR_TAVILY_API_KEY>"
# for help with debugging you can set export DEBUG=1
POETRY_BIN=$(which poetry) sudo -E bash evaluation/benchmarks/gaia/scripts/run_infer.sh [model_config] [git_version] [agent_name] [eval_limit] [gaia_subset] [num_workers] [split]
```

- `model_config`, e.g. `llm.claude4`, is the config group name for your LLM settings, as defined in your `config.toml` file
- `git_version` is the git commit hash of the OpenHands-Versa version you would like to evaluate, e.g. `HEAD`
- `agent_name` is the name of the agent to use, defaulting to `CodeActAgent`. OpenHands-Versa uses `CodeActAgent` for all its experiments.
- `eval_limit`, e.g. `10`, limits the evaluation to the first `eval_limit` instances, defaulting to all instances in the corresponding split of the GAIA dataset.
- `gaia_subset`, GAIA benchmark has multiple subsets: `2023_level1`, `2023_level2`, `2023_level3`, `2023_all`, defaulting to `2023_level1`.
- `num_workers`, e.g. `3`, is the number of parallel workers to run the evaluation. By default, it is set to 1.
- `split`, GAIA benchmark has two splits: `validation` and `test`, defaulting to `test`

An example command for running inference would be:
```bash
POETRY_BIN=$(which poetry) sudo -E bash evaluation/benchmarks/gaia/scripts/run_infer.sh llm.claude4 HEAD CodeActAgent 301 2023_all 1 test
```

**Note**: We have not tested using num_workers > 1. We always run evaluation sequentially using num_workers = 1, to avoid potential rate limit issues for the search API.

For very few cases (~10-15 out of 300 test samples), the OpenHands-Versa agent may crash due to various reasons (like Docker Runtime being disconnected or too much memory consumption during browsing), and we do not obtain any answer for these instances. To fix this, we find such instances and re-run them.

```bash
# Find all crashed instances and remove them from output.jsonl file
sudo -E python3 find_errors.py [output_path]
```
- `output_path`, path to output.jsonl file. You can find the output.jsonl file inside the directory: `evaluation/evaluation_outputs/outputs/gaia/...`.

After removing the crashed instances, you can simply re-run the command for starting evaluation using `run_infer.sh`. You can repeat this process many times till all errors are not resolved, but in practice we find that we don't need to re-run more than thrice. Also, some instances may still crash even after all re-runs, and our scripts report an empty string answer for such instances.

## Extract and Reformat Answer
Since GAIA performs string matching to compute accuracy and requires the agent's answer to match exactly with the ground truth, we use a simple LLM-based inference strategy that rephrases the answer if it doesn't follow the formatting instructions given in the task. For example, this approach will help with cases where the task asks that the numerical answer must be written in plain-text (eg: five hundred) but the agent answered in digits (eg: 500).

```bash
export LITELLM_BASE_URL="<Base URL of Your LLM API Endpoint>"
export LITELLM_API_KEY="<API Key of your LLM API Endpoint>"
python evaluation/benchmarks/gaia/process_answer.py --input-filename "<Path to output.jsonl file>" --output-filename "Path of the JSONL file where you want to save the processed outputs, eg: ./model_outputs_processed.jsonl" --model "LLM to use for reformatting answers (We use claude-3.7-sonnet for all our experiments)"
```

The above command will create a JSONL file which can be submitted to GAIA leaderboard for test set. The printed score in stdout will be correct only for the validation split and not the test split since ground-truth answers for test split are not open-source.
