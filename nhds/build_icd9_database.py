#!/usr/bin/python

import struct
import sqlite3

def get_db(database_name):
    db = sqlite3.connect(database_name)
    db.execute(('DROP TABLE IF EXISTS icd9'))
    db.execute(('CREATE TABLE icd9 ('
                '  code TEXT, '
                '  description TEXT '
                ')'))

    return db

def get_records(filename):
    fmtstring = "5sx"
    size = struct.calcsize(fmtstring)

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            icd9 = struct.unpack(fmtstring, line[:size])[0]
            description = line[size:]

            yield (icd9.decode("ISO-8859-1").strip(),
                   description.decode("ISO-8859-1"))

def main(filename, database_name):
    db = get_db(database_name)
    db.executemany(('INSERT INTO '
                    '  icd9 (code, description) '
                    'VALUES '
                    '  (?, ?)'),
                   get_records(filename))
    db.commit()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("database_name")
    args = parser.parse_args()

    main(**vars(args))
