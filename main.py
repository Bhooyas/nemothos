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
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path of the file to optimize",
)
@click.option("-t", "--task", type=str, help="Task to write code for")
@click.option("--run-id", type=str, help="Run id to store details")
def main(max_generation, hard, reasoning, file, task, run_id):

    if file is None and task is None:
        print("--file or --task needs to be passed")
        exit(1)
    elif file is None:
        if task.strip() == "":
            print("--task cannot be empty")
            exit(1)
        state = State(task=task, max_generation=max_generation)
    elif task is None:
        with open(file, "r") as f:
            state = State(code=f.read(), max_generation=max_generation)
    else:
        print("--file or --task only one can be passed")
        exit(1)

    if run_id is None:
        run_id = time.strftime("%d_%m_%Y_%H_%M_%S", time.localtime())

    model_name = "nemotron-3-nano:30b-cloud" if not hard else "nemotron-3-super:cloud"
    llm = ChatOllama(model=model_name, reasoning=reasoning)
    print(f"Initialized {model_name} with reasoning: {reasoning}")

    graph = get_graph(llm)

    state = graph.invoke(state)

    print("OPTIMIZED CODE")
    print(state["code"])

    with open(f"runs/{run_id}.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"State dumped to runs/{run_id}.json")


if __name__ == "__main__":
    main()
    