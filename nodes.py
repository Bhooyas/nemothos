import json
import time

from models import State
from prompts import (
    CODER_AGENT_PROMPT,
    OPTIMIZER_AGENT_PROMPT,
    PERFOMANCE_AGENT_PROMPT,
    SECURITY_AGENT_PROMPT,
)


def code_present(state: State) -> bool:
    if state.get("code") is None:
        return "CODE"
    return "SECURITY"


def create_generate_code(llm):

    def generate_code(state: State) -> State:

        print("Generating code")

        start = time.perf_counter()
        messages = [
            {"role": "system", "content": CODER_AGENT_PROMPT},
            {"role": "user", "content": state.get("task")},
        ]
        output = llm.invoke(messages)
        end = time.perf_counter()

        state["code"] = output.content
        state["messages"] = state.get("messages", []) + [output.model_dump()]

        print(f"Code Generation took {end - start} seconds")

        return state

    return generate_code


def create_security_agent(llm):

    def security_agent(state: State) -> State:

        state["generation"] = state.get("generation", 0) + 1

        print(
            f"Scanning code for security vulnerabilities {state['generation']}/{state['max_generation']}"
        )

        start = time.perf_counter()
        messages = [
            {"role": "system", "content": SECURITY_AGENT_PROMPT},
            {"role": "user", "content": state.get("code")},
        ]
        output = llm.invoke(messages)
        end = time.perf_counter()

        try:
            state["security_issues"] = json.loads(output.content)
            print(
                f"Scanned code for security vulnerabilities for {end - start} seconds found {len(state['security_issues'])}"
            )
        except Exception:
            state["security_issues"] = output.content
            print(
                f"Scanned code for security vulnerabilities for {end - start} seconds"
            )

        state["messages"] = state.get("messages", []) + [output.model_dump()]

        return state

    return security_agent


def create_performance_agent(llm):

    def performance_agent(state: State) -> State:

        print(
            f"Scaning code for performance vulnerabilities {state['generation']}/{state['max_generation']}"
        )

        start = time.perf_counter()
        messages = [
            {"role": "system", "content": PERFOMANCE_AGENT_PROMPT},
            {"role": "user", "content": state.get("code")},
        ]
        output = llm.invoke(messages)
        end = time.perf_counter()

        try:
            state["performance_issues"] = json.loads(output.content)
            print(
                f"Scaned code for performance vulnerabilities for {end - start} seconds found {len(state['performance_issues'])}"
            )
        except Exception:
            state["performance_issues"] = output.content
            print(
                f"Scaned code for performance vulnerabilities for {end - start} seconds"
            )

        state["messages"] = state.get("messages", []) + [output.model_dump()]

        return state

    return performance_agent


def create_optimizer(llm):

    def optimizer(state: State) -> State:

        print(f"Optimizing code {state['generation']}/{state['max_generation']}")

        start = time.perf_counter()
        messages = [
            {"role": "system", "content": OPTIMIZER_AGENT_PROMPT},
            {
                "role": "user",
                "content": f"Code:\nf{state.get('code')}\n\nSecurity Issues:\nf{state.get('security_issues')}\n\nPerformance Issues:\nf{state.get('performance_issues')}",
            },
        ]
        output = llm.invoke(messages)
        end = time.perf_counter()

        state["code"] = output.content
        state["messages"] = state.get("messages", []) + [output.model_dump()]

        print(f"Code Optimized for {end - start} seconds")

        return state

    return optimizer


def improve_more(state: State) -> str:
    if (not state["performance_issues"] and not state["security_issues"]) or state[
        "generation"
    ] >= state["max_generation"]:
        return "END"
    return "continue"
