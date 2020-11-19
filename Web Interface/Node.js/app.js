const express = require('express');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const db = new sqlite3.Database('/home/pi/CyberTank/CyberTankDB');

app.get('/data', (req, res) => {

    res.setHeader('Access-Control-Allow-Origin', '*');

    const sql = 'select * from tankLevel';
    const params = [];

    db.all(sql, params, (err, rows) => {

        if (err) {

            res.status(400).json({ 'error': err.message });
            return;
        }

        if (!rows) {

            res.status(204).json({ 'error': 'No cities found' });
            return;
        }

        res.json({
            //'message': 'success',
            rows
        });
    });
});


const server = app.listen(3000, () => {

    console.log('Application started on port 3000');
});

process.on('SIGINT', () => {

    db.close((err) => {

        console.log('Application terminating');

        if (err) {
            console.error(err.message);
        }
        console.log('Closing the database connection.');
    });

    server.close();
});