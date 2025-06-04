# Development Guide

## Start the Server for Development
### 1. Requirements
* Linux, Mac OS, or [WSL on Windows](https://learn.microsoft.com/en-us/windows/wsl/install)  [Ubuntu >= 22.04]
* [Docker](https://docs.docker.com/engine/install/) (For those on MacOS, make sure to allow the default Docker socket to be used from advanced settings!)
* [Python](https://www.python.org/downloads/) = 3.12
* [NodeJS](https://nodejs.org/en/download/package-manager) >= 20.x
* [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) >= 1.8
* OS-specific dependencies:
  - Ubuntu: build-essential => `sudo apt-get install build-essential`
  - WSL: netcat => `sudo apt-get install netcat`

Make sure you have all these dependencies installed before moving on to `make build`.

```bash
# Download and install Mamba (a faster version of conda)
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh

# Install Python 3.12, nodejs, and poetry
mamba install python=3.12
mamba install conda-forge::nodejs
mamba install conda-forge::poetry
```

### 2. Build and Setup The Environment
Begin by building the project which includes setting up the environment and installing dependencies. This step ensures that OpenHands-Versa is ready to run on your system:

```bash
make build
```

### 3. Configuring the Language Model
OpenHands-Versa supports a diverse array of Language Models (LMs) through the powerful [litellm](https://docs.litellm.ai) library.

To configure the LM of your choice, run:

   ```bash
   make setup-config
   ```

   This command will prompt you to enter the LLM API key, model name, and other variables ensuring that OpenHands-Versa is tailored to your specific needs.

**Note on Alternative Models:**
See [OpenHands documentation](https://docs.all-hands.dev/modules/usage/llms) for recommended models.

### 4. Debugging
If you encounter any issues with the Language Model (LM) or you're simply curious, export DEBUG=1 in the environment and restart the evaluation.
OpenHands-Versa will log the prompts and responses in the logs/llm/CURRENT_DATE directory, allowing you to identify the causes.