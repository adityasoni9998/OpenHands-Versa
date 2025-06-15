# Evaluating OpenHands-Versa on The Agent Company


This folder contains the evaluation harness The Agent Company benchmark. It is built on top of the original harness from [The Agent Company](https://github.com/TheAgentCompany/TheAgentCompany/tree/main/evaluation) ([paper](https://arxiv.org/abs/2412.14161)).

The evaluation consists of three steps:

1. Environment setup: [install python environment and configure LLM config](../../../README.md#installation), and [launch services](https://github.com/TheAgentCompany/TheAgentCompany/blob/main/docs/SETUP.md). Make sure you have an API Key to Tavily Search API.
2. [Run Evaluation](#run-inference-on-the-agent-company-tasks): Run inference on all tasks.
3. [Generating Summary of Results](#generating-summary-of-results)

> [!NOTE]
> **Known issues**
>
> If the machine on which the services are hosted is slow, the NPCs may not respond or the websites may become non-responsive. We use AWS EC2 instances (t3.2xlarge) for all our experiments and do not encounter this issue.
> For one of the litellm proxies we used, we found that the proxy raised Cloudflare errors when agent tried visiting Gitlab. These errors are silent and not detected by the evaluation scripts.

## Setup Environment and LLM Configuration

Please follow instruction [here](../../../README.md#installation-and-llm-configuration) to setup your local development environment and LLM.

## Run Inference on The Agent Company Tasks

When the `run_infer.sh` script is started, it will automatically pull all task images. Every task image will be used to create an OpenHands runtime image where the agent will operate on. Run the following command from the root directory of the repository:

```bash
export SEARCH_API_KEY=<TAVILY SEARCH API KEY>
POETRY_BIN=$(which poetry) sudo -E bash evaluation/benchmarks/the_agent_company/scripts/run_infer.sh \
  --agent-llm-config <agent-llm-config, default to 'agent'>  \
  --env-llm-config <env-llm-config, default to 'env'> \
  --outputs-path <outputs-path, default to outputs> \
  --server-hostname <server-hostname, default to localhost> \
  --version <version, default to 1.0.0> \
  --start-percentile <integer from 0 to 99, default to 0> \
  --end-percentile <integer from 1 to 100, default to 100>


# Example
POETRY_BIN=$(which poetry) sudo -E bash evaluation/benchmarks/the_agent_company/scripts/run_infer.sh \
  --agent-llm-config llm.claude4 \
  --env-llm-config llm.claude_3_5 \
  --outputs-path outputs \
  --server-hostname localhost \
  --version 1.0.0 \
  --start-percentile 10 \
  --end-percentile 20
```

- `agent-llm-config`: the config name for the agent LLM. This should match the config name in config.toml. This is the LLM used by the agent (e.g. CodeActAgent).
- `env-llm-config`: the config name for the environment LLM. This should match the config name in config.toml. This is used by the chat bots (NPCs) and LLM-based evaluators. To allow for direct comparison with all baseline results, it is recommended to use `claude-3-5-sonnet-20241022` as the environment LLM.
- `outputs-path`: the path to save trajectories and evaluation results.
- `server-hostname`: the hostname of the server that hosts all the web services. It could be localhost if you are running the evaluation and services on the same machine. If the services are hosted on a remote machine, you must use the hostname of the remote machine rather than IP address.
- `version`: the version of the task images to use. Currently, the only supported version is 1.0.0.
- `start-percentile`: the start percentile of the task split, must be an integer between 0 to 99.
- `end-percentile`: the end percentile of the task split, must be an integer between 1 to 100 and larger than start-percentile.

The script is idempotent. If you run it again, it will resume from the last checkpoint. It would usually take 2 days to finish evaluation if you run the whole task set.
To speed up evaluation, you can use `start-percentile` and `end-percentile` to split the tasks for higher parallelism, provided concurrent runs are **targeting different servers**.

Note: the script will automatically skip a task if it encounters an error. This usually happens when the OpenHands runtime dies due to some unexpected errors. This means even if the script finishes, it might not have evaluated all tasks. You can manually resume the evaluation by running the script again.

## Generating Summary of Results

To obtain evaluation report containing detailed summary of results, please run the following command:

```bash
python evaluation/benchmarks/the_agent_company/scripts/summarise_results.py [output_directory]
```
- output_directory: path to the directory containing The Agent Company outputs. This path corresponds to the `outputs-path` field used in `run_infer.sh`.
