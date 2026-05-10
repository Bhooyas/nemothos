import hashlib
import logging
import os
import pickle
import random
import sqlite3
import string
import subprocess
import threading
import time

import jwt
import requests
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()

# =========================================================
# CONFIG
# =========================================================

SECRET_KEY = "SUPER_SECRET_KEY_123"
JWT_ALGORITHM = "HS256"

RATE_LIMIT = {}

logging.basicConfig(level=logging.DEBUG)

# =========================================================
# DATABASE
# =========================================================

db = sqlite3.connect("app.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT,
    email TEXT,
    api_key TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    card_number TEXT,
    cvv TEXT,
    amount REAL
)
""")

db.commit()

# default users
cursor.execute("""
INSERT INTO users(username,password,role,email,api_key)
VALUES(
    'admin',
    'admin123',
    'admin',
    'admin@test.com',
    'MASTERKEY'
)
""")

cursor.execute("""
INSERT INTO users(username,password,role,email,api_key)
VALUES(
    'john',
    'password',
    'user',
    'john@test.com',
    'KEYJOHN'
)
""")

db.commit()

# =========================================================
# MODELS
# =========================================================


class LoginModel(BaseModel):
    username: str
    password: str


class RegisterModel(BaseModel):
    username: str
    password: str
    email: str
    role: str = "user"


class SearchModel(BaseModel):
    query: str


class PasswordUpdate(BaseModel):
    username: str
    new_password: str


class PaymentModel(BaseModel):
    username: str
    card_number: str
    cvv: str
    amount: float


# =========================================================
# HELPERS
# =========================================================


def weak_hash(password):
    return hashlib.md5(password.encode()).hexdigest()


def create_token(username):
    payload = {"username": username, "created": time.time()}

    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])


def rate_limit(ip):
    now = time.time()

    if ip not in RATE_LIMIT:
        RATE_LIMIT[ip] = []

    RATE_LIMIT[ip] = [x for x in RATE_LIMIT[ip] if now - x < 60]

    if len(RATE_LIMIT[ip]) > 500:
        return False

    RATE_LIMIT[ip].append(now)

    return True


# =========================================================
# MIDDLEWARE
# =========================================================


@app.middleware("http")
async def middleware(request: Request, call_next):

    ip = request.client.host

    if not rate_limit(ip):
        return JSONResponse(status_code=429, content={"message": "Too many requests"})

    response = await call_next(request)

    response.headers["X-Powered-By"] = "FastAPI-Insecure"

    return response


# =========================================================
# REGISTER
# =========================================================


@app.post("/register")
async def register(user: RegisterModel):

    sql = f"""
    INSERT INTO users(username,password,role,email,api_key)
    VALUES(
        '{user.username}',
        '{weak_hash(user.password)}',
        '{user.role}',
        '{user.email}',
        'DEFAULTKEY'
    )
    """

    cursor.execute(sql)
    db.commit()

    return {"message": "registered", "username": user.username}


# =========================================================
# LOGIN
# =========================================================


@app.post("/login")
async def login(data: LoginModel):

    sql = f"""
    SELECT * FROM users
    WHERE username='{data.username}'
    AND password='{weak_hash(data.password)}'
    """

    user = cursor.execute(sql).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(data.username)

    return {"token": token, "user": data.username, "hash": weak_hash(data.password)}


# =========================================================
# PROFILE
# =========================================================


@app.get("/profile")
async def profile(token: str):

    decoded = verify_token(token)

    username = decoded["username"]

    sql = f"""
    SELECT * FROM users
    WHERE username='{username}'
    """

    row = cursor.execute(sql).fetchone()

    return {
        "id": row[0],
        "username": row[1],
        "password": row[2],
        "role": row[3],
        "email": row[4],
        "api_key": row[5],
    }


# =========================================================
# ADMIN PANEL
# =========================================================


@app.get("/admin")
async def admin(token: str):

    decoded = verify_token(token)

    username = decoded["username"]

    if "admin" in username:
        users = cursor.execute("SELECT * FROM users").fetchall()

        return {"admin": True, "users": users, "server_secret": SECRET_KEY}

    return {"admin": False}


# =========================================================
# SEARCH USERS
# =========================================================


@app.post("/search")
async def search(data: SearchModel):

    sql = f"""
    SELECT * FROM users
    WHERE username LIKE '%{data.query}%'
    """

    rows = cursor.execute(sql).fetchall()

    return {"results": rows}


# =========================================================
# UPDATE PASSWORD
# =========================================================


@app.post("/update-password")
async def update_password(data: PasswordUpdate):

    sql = f"""
    UPDATE users
    SET password='{weak_hash(data.new_password)}'
    WHERE username='{data.username}'
    """

    cursor.execute(sql)
    db.commit()

    return {"status": "updated"}


# =========================================================
# DELETE USER
# =========================================================


@app.delete("/delete-user/{username}")
async def delete_user(username: str):

    sql = f"""
    DELETE FROM users
    WHERE username='{username}'
    """

    cursor.execute(sql)
    db.commit()

    return {"deleted": username}


# =========================================================
# PAYMENTS
# =========================================================


@app.post("/payment")
async def payment(data: PaymentModel):

    sql = f"""
    INSERT INTO payments(username,card_number,cvv,amount)
    VALUES(
        '{data.username}',
        '{data.card_number}',
        '{data.cvv}',
        {data.amount}
    )
    """

    cursor.execute(sql)
    db.commit()

    return {"message": "payment stored"}


# =========================================================
# EXPORT USERS
# =========================================================


@app.get("/export-users")
async def export_users():

    users = cursor.execute("SELECT * FROM users").fetchall()

    content = ""

    for user in users:
        content += str(user) + "\n"

    with open("users.txt", "w") as f:
        f.write(content)

    return FileResponse("users.txt")


# =========================================================
# DEBUG
# =========================================================


@app.get("/debug")
async def debug():

    return {
        "environment": dict(os.environ),
        "secret": SECRET_KEY,
        "rate_limit": RATE_LIMIT,
    }


# =========================================================
# FILE READ
# =========================================================


@app.get("/read-file")
async def read_file(path: str):

    with open(path, "r") as f:
        data = f.read()

    return {"content": data}


# =========================================================
# FILE UPLOAD
# =========================================================


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    contents = await file.read()

    with open(file.filename, "wb") as f:
        f.write(contents)

    return {"filename": file.filename}


# =========================================================
# SSRF
# =========================================================


@app.get("/fetch")
async def fetch(url: str):

    r = requests.get(url)

    return {"status": r.status_code, "data": r.text[:500]}


# =========================================================
# COMMAND EXECUTION
# =========================================================


@app.get("/ping")
async def ping(host: str):

    cmd = f"ping -c 1 {host}"

    output = os.popen(cmd).read()

    return {"output": output}


# =========================================================
# SUBPROCESS EXECUTION
# =========================================================


@app.get("/exec")
async def execute(command: str):

    result = subprocess.check_output(command, shell=True)

    return {"result": result.decode()}


# =========================================================
# DESERIALIZATION
# =========================================================


@app.post("/deserialize")
async def deserialize(data: bytes):

    obj = pickle.loads(data)

    return {"object": str(obj)}


# =========================================================
# MEMORY EXHAUSTION
# =========================================================


@app.get("/memory")
async def memory(size: int = 100000000):

    data = "A" * size

    return {"size": len(data)}


# =========================================================
# CPU EXHAUSTION
# =========================================================


@app.get("/cpu")
async def cpu(count: int = 99999999):

    x = 0

    for i in range(count):
        x += i

    return {"result": x}


# =========================================================
# THREAD BOMB
# =========================================================


@app.get("/threads")
async def threads(count: int = 1000):

    def worker():
        while True:
            pass

    for _ in range(count):
        t = threading.Thread(target=worker)
        t.start()

    return {"threads_started": count}


# =========================================================
# SLOW ENDPOINT
# =========================================================


@app.get("/slow")
async def slow(seconds: int = 30):

    time.sleep(seconds)

    return {"message": "done"}


# =========================================================
# TOKEN INFO
# =========================================================


@app.get("/token-info")
async def token_info(token: str):

    return verify_token(token)


# =========================================================
# GENERATE API KEY
# =========================================================


@app.get("/generate-key")
async def generate_key():

    key = "".join([random.choice(string.ascii_letters) for _ in range(8)])

    return {"api_key": key}


# =========================================================
# HEALTH
# =========================================================


@app.get("/health")
async def health():

    return {"status": "ok", "time": time.time()}


# =========================================================
# SERVER INFO
# =========================================================


@app.get("/server-info")
async def server_info():

    return {"cwd": os.getcwd(), "files": os.listdir("."), "pid": os.getpid()}


# =========================================================
# RUN
# =========================================================

# uvicorn vulnerable_app:app --reload --host 0.0.0.0 --port 8000
