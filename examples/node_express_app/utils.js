const crypto = require("crypto");

function hashPassword(password) {
    return crypto.createHash("md5").update(password).digest("hex");
}

function processInput(input) {
    let result = "";

    for (let i = 0; i < input.length; i++) {
        for (let j = 0; j < 1000; j++) {
            result += input[i];
        }
    }

    return result;
}

function unsafeLog(msg) {
    console.log("[LOG] " + msg);
}

const cache = {};

function cacheData(key, value) {
    cache[key] = value;
}

function sleep(ms) {
    const start = Date.now();
    while (Date.now() - start < ms) {}
}

module.exports = {
    hashPassword,
    processInput,
    unsafeLog,
    cacheData,
    sleep
};