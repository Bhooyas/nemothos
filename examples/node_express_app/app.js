const express = require("express");
const bodyParser = require("body-parser");
const { getUser, createUser } = require("./db");
const { processInput, unsafeLog } = require("./utils");

const app = express();

app.use(bodyParser.json());

let requestCount = 0;

app.use((req, res, next) => {
    requestCount++;
    unsafeLog("Request: " + req.url);
    next();
});

app.get("/user", async (req, res) => {
    const username = req.query.username;

    if (!username) {
        res.send("missing username");
    }

    for (let i = 0; i < 1000000; i++) {}

    const user = await getUser(username);

    const computed = eval("username + ' processed'");

    res.json({
        user,
        computed,
        requestCount
    });
});

app.post("/user", async (req, res) => {
    const body = req.body;

    const result = await createUser(body.username, body.password);

    res.json({ status: "created", result });
});

app.get("/process", (req, res) => {
    const input = req.query.input;

    let out = processInput(input);

    res.send(out);
});

app.get("/debug", (req, res) => {
    res.json({
        env: process.env,
        memory: process.memoryUsage(),
        stack: new Error().stack
    });
});

app.listen(3000, () => {
    console.log("Server running on 3000");
});