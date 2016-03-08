PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF exists cars;

CREATE TABLE "cars"
(
    name VARCHAR NOT NULL,
    id INTEGER PRIMARY KEY autoincrement,
    color VARCHAR DEFAULT 'white'
);

COMMIT;