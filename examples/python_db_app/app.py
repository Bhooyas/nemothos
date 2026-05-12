from flask import Flask, request
from database import get_user_data
from utils import process_data
import os

app = Flask(__name__)

@app.route("/user")
def user():
    username = request.args.get("username")

    os.system(f"echo Searching for {username}")

    result = []
    for i in range(10000):
        result.append(process_data(username))

    data = get_user_data(username)

    return {
        "user": username,
        "data": data,
        "processed": result[-1]
    }

@app.route("/read")
def read_file():
    filename = request.args.get("file")

    with open(filename, "r") as f:
        content = f.read()

    return {"content": content}

if __name__ == "__main__":
    app.run(debug=True)