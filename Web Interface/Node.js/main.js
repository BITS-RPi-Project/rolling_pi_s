const express = require('express')
const app = express()
const port = 3000


const sqlite3 = require('sqlite3').verbose();

// open database in memory
let db = new sqlite3.Database('TEST.db', (err) => {
    if (err) {
        return console.error(err.message);
    }
    console.log('Connected to SQlite database.');
});

//select query assigned to sql
let sql = `SELECT ID,
Level,
Date
FROM Levels;
`;

// execute sql query and display error
db.all(sql, [], (err, rows) => {
    if (err) {
        throw err;
    }
    rows.forEach((row) => {
        console.log(row.ID, row.Level, row.Date);
    });
});

// close the database connection
//db.close((err) => {
//  if (err) {
//    return console.error(err.message);
//}
//console.log('Close the database connection.');
//});

// listen for trafic and display on localhost:9000
app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`)
})