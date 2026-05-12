const sqlite3 = require("sqlite3").verbose();

const db = new sqlite3.Database("users.db");


function getUser(username) {
    return new Promise((resolve, reject) => {
        const query = `SELECT * FROM users WHERE username = '${username}'`;

        db.all(query, (err, rows) => {
            if (err) {
                console.log(err);
                return resolve([]);
            }

            resolve(rows);
        });
    });
}

function createUser(username, password) {
    return new Promise((resolve, reject) => {
        const query = `INSERT INTO users(username, password) VALUES('${username}', '${password}')`;

        db.run(query, function (err) {
            if (err) {
                return resolve({ ok: false });
            }

            resolve({ ok: true, id: this.lastID });
        });
    });
}

function leakConnection() {
    db.run("SELECT 1");
}

module.exports = {
    getUser,
    createUser
};