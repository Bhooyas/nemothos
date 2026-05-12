import json
import time

import click
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from models import State
from nodes import (
    code_present,
    create_generate_code,
    create_optimizer,
    create_performance_agent,
    create_security_agent,
    improve_more,
)
import os
import re

EXCLUDE_PATHS = [
    # =========================================
    # Version Control
    # =========================================
    ".git",
    ".svn",
    ".hg",
    ".bzr",

    # Git internals
    ".git/objects",
    ".git/hooks",
    ".git/logs",
    ".git/index",

    # =========================================
    # Python
    # =========================================
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".coverage",
    "htmlcov",
    ".hypothesis",
    ".pyre",
    ".venv",
    "venv",
    "env",
    "ENV",
    ".env",
    ".env.*",
    ".ipynb_checkpoints",

    # =========================================
    # Node.js / JavaScript
    # =========================================
    "node_modules",
    ".npm",
    ".pnpm-store",
    ".yarn",
    ".yarn-cache",
    ".next",
    ".nuxt",
    ".parcel-cache",
    ".turbo",
    ".svelte-kit",
    "dist",
    "build",
    "coverage",
    ".eslintcache",

    # =========================================
    # Java / Kotlin
    # =========================================
    ".gradle",
    "build",
    "out",
    "*.class",
    "*.jar",
    "*.war",
    "*.ear",

    # =========================================
    # Go
    # =========================================
    "vendor",
    "*.test",
    "*.out",

    # =========================================
    # Rust
    # =========================================
    "target",
    "Cargo.lock",

    # =========================================
    # C / C++ / CMake
    # =========================================
    "cmake-build-*",
    "CMakeFiles",
    "CMakeCache.txt",
    "compile_commands.json",
    "Makefile",
    "*.o",
    "*.obj",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.exe",
    "*.a",
    "*.lib",

    # =========================================
    # Swift / Xcode
    # =========================================
    ".build",
    "DerivedData",
    "*.xcworkspace",
    "*.xcuserdata",
    "*.xcuserstate",

    # =========================================
    # Terraform / IaC
    # =========================================
    ".terraform",
    ".terraform.lock.hcl",
    "*.tfstate",
    "*.tfstate.*",

    # =========================================
    # Docker / Containers
    # =========================================
    ".docker",
    "docker-data",

    # =========================================
    # IDE / Editors
    # =========================================
    ".idea",
    ".vscode",
    ".fleet",
    ".history",
    "*.swp",
    "*.swo",
    "*~",

    # =========================================
    # OS Files
    # =========================================
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",

    # =========================================
    # Logs
    # =========================================
    "*.log",
    "logs",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    "pnpm-debug.log*",

    # =========================================
    # Secrets / Credentials
    # =========================================
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".secrets",
    "secrets",
    "*.pem",
    "*.key",
    "*.crt",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_dsa",
    "id_ed25519",
    ".ssh",
    ".gnupg",
    ".aws",
    ".azure",
    ".kube",

    # =========================================
    # Databases / Binary Data
    # =========================================
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.mdb",
    "*.parquet",
    "*.feather",

    # =========================================
    # Archives
    # =========================================
    "*.zip",
    "*.tar",
    "*.gz",
    "*.7z",
    "*.rar",

    # =========================================
    # Media
    # =========================================
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.svg",
    "*.ico",
    "*.mp4",
    "*.mp3",
    "*.wav",
    "*.mov",

    # =========================================
    # ML / AI Models
    # =========================================
    "*.onnx",
    "*.pt",
    "*.pth",
    "*.ckpt",
    "*.safetensors",

    # =========================================
    # Temporary Files
    # =========================================
    "tmp",
    "temp",
    ".cache",
    ".sass-cache",

    # =========================================
    # System Directories (IMPORTANT)
    # =========================================
    "/proc",
    "/sys",
    "/dev",
    "/run",
    "/tmp",

    # =========================================
    # User Privacy
    # =========================================
    "~/Documents",
    "~/Downloads",
    "~/Desktop",
    "~/Pictures",
    "~/Videos",

    # =========================================
    # Large Generated Assets
    # =========================================
    "public/build",
    "storybook-static",
    ".docusaurus",

    # =========================================
    # Lockfiles (optional)
    # =========================================
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
]

ALLOWED_EXTENSIONS = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".sh", ".bash")

def get_graph(llm: ChatOllama) -> StateGraph:
    graph = StateGraph(State)
    graph.add_node(code_present)
    graph.add_node("generate_code", create_generate_code(llm))
    graph.add_node("security_agent", create_security_agent(llm))
    graph.add_node("performance_agent", create_performance_agent(llm))
    graph.add_node("optimizer", create_optimizer(llm))
    graph.add_node(improve_more)
    graph.add_conditional_edges(
        START, code_present, {"CODE": "generate_code", "SECURITY": "security_agent"}
    )
    graph.add_edge("generate_code", "security_agent")
    graph.add_edge("security_agent", "performance_agent")
    graph.add_edge("performance_agent", "optimizer")
    graph.add_conditional_edges(
        "optimizer", improve_more, {"continue": "security_agent", "END": END}
    )
    graph = graph.compile()
    return graph


@click.command()
@click.option(
    "-m",
    "--max-generation",
    type=int,
    default=3,
    help="Number of times to run the loop",
)
@click.option(
    "--hard",
    type=bool,
    is_flag=True,
    default=False,
    help="Use higher model and optimize harder",
)
@click.option("--reasoning", type=bool, default=True, help="Use model with reasoning")
@click.option("-d", "--directory", type=click.Path(exists=True, dir_okay=True, file_okay=False), help="Path of directory to optimize")
@click.option("-e", "--exclude", type=str, help="Comma seprated file or folders to ignore")
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path of the file to optimize",
)
@click.option("-t", "--task", type=str, help="Task to write code for")
@click.option("-o", "--overwrite", type=bool, default=False, help="Overwrite the input file/folders, defult false")
@click.option("--run-id", type=str, help="Run id to store details")
def main(max_generation, hard, reasoning, directory, exclude, file, task, overwrite, run_id):
    if directory is None and file is None and task is None:
        print("--directory or --file or --task needs to be passed")
        exit(1)
    elif directory:
        codes = []
        if exclude:
            local_exclude = EXCLUDE_PATHS + exclude.split(",")
        else:
            local_exclude = EXCLUDE_PATHS
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in local_exclude]
            for f in files:
                if f not in local_exclude and f.endswith(ALLOWED_EXTENSIONS):
                    codes.append(os.path.join(root, f))
        print(f"Code files being optimized: {codes}")
        code = ""
        for file_name in codes:
            with open(file_name, "r") as f:
                code += f"```{file_name}\n{f.read()}\n```"
        state = State(code=code, max_generation=max_generation)
    elif file:
        with open(file, "r") as f:
            state = State(code=f"```{file}\n{f.read()}\n```", max_generation=max_generation)
    else:
        if task.strip() == "":
            print("--task cannot be empty")
            exit(1)
        state = State(task=task, max_generation=max_generation)
    if run_id is None:
        run_id = time.strftime("%d_%m_%Y_%H_%M_%S", time.localtime())

    model_name = "nemotron-3-nano:30b-cloud" if not hard else "nemotron-3-super:cloud"
    llm = ChatOllama(model=model_name, reasoning=reasoning)
    print(f"Initialized {model_name} with reasoning: {reasoning}")

    graph = get_graph(llm)

    state = graph.invoke(state)

    with open(f"runs/{run_id}.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"State dumped to runs/{run_id}.json")

    if overwrite:
        print("Writing code to files")
        if state["code"].startswith("````"):
            pattern = r"````([^\n]+)\n(.*?)````"
        else:
            # pattern = r"```([^\n]+)\n(.*?)```"
            start = ""
            for i in state["code"]:
                if i == "`":
                    start += i
            pattern = f"{start}([^\n]+)\n(.*?){start}"
            print(pattern)
        matches = re.findall(pattern, state["code"], re.DOTALL)
        for file_name, code in matches:
            print(f"updating {file_name}")
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(code)
        print("Updated the files")
    else:
        print("OPTIMIZED CODE")
        print(state["code"])


if __name__ == "__main__":
    main()
    