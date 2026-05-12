# Nemothos - Enhanced Code Optimization

![Nemothos](https://socialify.git.ci/Bhooyas/nemothos/image?font=KoHo&language=1&name=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

A repository trying to replicate Mythos model type performance using NVIDIA Nemotron Models. The repository aims to find security and performace vulnerabilites in the code and optimize it across entire directories.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Bhooyas/nemothos.git
cd nemothos
```

### 2. Install dependencies

It is recommended to use a virtual environment.

```bash
pip install -r requirements.txt
```

### 3. Install Ollama

Download and install Ollama from:

* [https://ollama.com/](https://ollama.com/)

After installation, authenticate using:

```bash
ollama signin
```

---

## Default Models

Nemothos uses the following models:

| Mode              | Model                       |
| ----------------- | --------------------------- |
| Default           | `nemotron-3-nano:30b-cloud` |
| Hard Optimization | `nemotron-3-super:cloud`    |

Use the `--hard` flag for deeper and more aggressive optimization passes.

---

## Usage

### Optimize a directory

Analyze and optimize all supported code files inside a directory.

```bash
python main.py --directory ./examples/python_db_app --overwrite true
```

### Optimize a single file

```bash
python main.py --file test.py
```

### Generate and optimize code from a task

```bash
python main.py --task "Write a FastAPI application with SQL authentication and rate limiting"
```
**Note**: Based on our observations using `nemotron-3-nano:30b-cloud` for 3-5 generations works the best. 

---

## Examples

The repository includes example projects inside the [`examples/`](examples) directory.

---

## CLI Options

```bash
Options:
  -m, --max-generation INTEGER   Number of optimization generations to run
  --hard                         Use a larger model for deeper optimization
  --reasoning BOOLEAN            Enable reasoning-capable models
  -d, --directory DIRECTORY      Path to the directory to optimize
  -e, --exclude TEXT             Comma-separated files or folders to exclude
  -f, --file FILE                Path to the file to optimize
  -t, --task TEXT                Generate code from a task prompt
  -o, --overwrite BOOLEAN        Overwrite input files/folders
                                 Default: false
  --run-id TEXT                  Custom run identifier for logs and outputs
  --help                         Show help message and exit
```

---

## Disclaimer

Nemothos is an experimental AI-assisted optimization tool.

Always review and validate generated or modified code before using it in production environments. Automated optimizations may introduce unintended behavioral or security changes.
