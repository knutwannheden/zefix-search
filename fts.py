import csv
import os
import sqlite3
import sys
from os import walk

import ndjson
from dotenv import dotenv_values

config = {**dotenv_values(".env"), **os.environ}
conn = sqlite3.connect(config["DB_FILE"])
cur = conn.cursor()

cur.execute('create virtual table zefix using fts5(company_name, company_ehraid, company_chid, publ_date, publ_id, publ_message)')


def insert_csv_batch(chunk):
    cur.executemany('insert into zefix(company_chid, publ_date, publ_id, publ_message) values (?,?,?,?)', chunk)


def insert_json_batch(chunk):
    cur.executemany('insert into zefix(company_name, company_ehraid, publ_date, publ_id, publ_message) values (?,?,?,?,?)',
                    [(r['companyShort']['name'], r['companyShort']['ehraid'], r['sogcPublication']['registryOfCommerceJournalDate'],
                      r['sogcPublication']['sogcId'], r['sogcPublication']['message']) for r in chunk])


chunk_size = 10000
chunk = []

with open('pub.csv', 'r') as f:
    csv.field_size_limit(sys.maxsize)
    r = csv.reader(f, delimiter='\t')
    next(r)
    for i, row in enumerate(r):
        if i % chunk_size == 0 and i > 0:
            insert_csv_batch(chunk)
            chunk = []
            print(i)
        chunk.append(row)
    insert_csv_batch(chunk)

i = 0
for (dirpath, dirnames, filenames) in walk('zefix'):
    for filename in filenames:
        if filename.endswith('.ndjson'):
            with open(dirpath + '/' + filename, 'r') as f:
                data = ndjson.load(f)
                insert_json_batch(data)
                i += len(data)
                print(i)

conn.commit()
conn.close()
