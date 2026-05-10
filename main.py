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

# state = State(code="""# FastAPI app with health & rate-limited webhook
# from fastapi import FastAPI
# from starlette.middleware.limiter import RateLimitMiddleware

# app = FastAPI()
# app.add_middleware(RateLimitMiddleware, key="webhook", limit=100, time_period=60)

# @app.get("/health")
# async def health():
#     return {"status": "ok"}

# @app.get("/webhook")
# async def webhook():
#     return {"msg": "received"}
# """)

# state = State(code="""```python
# # FastAPI app with health check and 60‑second per‑IP rate limit on /webhook
# from fastapi import FastAPI, Request, HTTPException
# from datetime import datetime, timezone

# app = FastAPI()
# _last = {}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/webhook")
# async def webhook(request: Request):
#     ip = request.client.host
#     ts = datetime.now(timezone.utc).timestamp()
#     if ip in _last and ts - _last[ip] < 60:
#         _last[ip] = ts
#         raise HTTPException(status_code=429, detail="rate limited")
#     _last[ip] = ts
#     return {"received": True}
# ```""")

# state = State(code='''from flask import Flask, request
# import sqlite3
# import hashlib
# import time

# app = Flask(__name__)

# # Global cache (not thread safe)
# cache = {}

# DATABASE = "users.db"


# def get_db():
#     return sqlite3.connect(DATABASE)


# @app.route("/login", methods=["POST"])
# def login():
#     username = request.form.get("username")
#     password = request.form.get("password")

#     conn = get_db()
#     cursor = conn.cursor()

#     # SQL Injection vulnerability
#     query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
#     cursor.execute(query)

#     user = cursor.fetchone()

#     conn.close()

#     if user:
#         return f"Welcome {username}"
#     else:
#         return "Invalid credentials"


# @app.route("/users")
# def users():
#     conn = get_db()
#     cursor = conn.cursor()

#     # Performance issue: SELECT *
#     cursor.execute("SELECT * FROM users")

#     rows = cursor.fetchall()

#     result = ""

#     # Performance issue: string concatenation in loop
#     for row in rows:
#         result += str(row) + "\n"

#     conn.close()

#     return result


# @app.route("/hash")
# def slow_hash():
#     text = request.args.get("text", "")

#     # CPU-heavy unnecessary work
#     result = text

#     for _ in range(100000):
#         result = hashlib.sha256(result.encode()).hexdigest()

#     return result


# @app.route("/search")
# def search():
#     query = request.args.get("q", "")

#     # Fake expensive operation
#     time.sleep(2)

#     if query in cache:
#         return cache[query]

#     conn = get_db()
#     cursor = conn.cursor()

#     # SQL injection again
#     sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"

#     cursor.execute(sql)
#     rows = cursor.fetchall()

#     conn.close()

#     response = str(rows)

#     cache[query] = response

#     return response


# @app.route("/profile/<user_id>")
# def profile(user_id):
#     conn = get_db()
#     cursor = conn.cursor()

#     # Missing validation
#     cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

#     user = cursor.fetchone()

#     conn.close()

#     # Potential crash
#     return f"""
#     <h1>{user[1]}</h1>
#     <p>Email: {user[2]}</p>
#     """


# @app.route("/calc")
# def calc():
#     expression = request.args.get("expr")

#     # Critical remote code execution vulnerability
#     return str(eval(expression))


# if __name__ == "__main__":
#     app.run(debug=True)''')

# # state = State(task="Write fast api code with health endpoint and a /webhook which has rate limiting implemented")
# state = graph.invoke(state)

# print("==" * 20)
# print("OPTIMIZED CODE:")
# print(state["code"])
