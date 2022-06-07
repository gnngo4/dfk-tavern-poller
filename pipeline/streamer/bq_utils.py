import os

from google.cloud import bigquery

TABLE_SCHEMA = [
        bigquery.SchemaField('user_address',"STRING",mode="REQUIRED"),
        bigquery.SchemaField('id',"STRING",mode="REQUIRED"),
        bigquery.SchemaField('price',"FLOAT",mode="REQUIRED"),
        bigquery.SchemaField('transaction_hash',"STRING",mode="REQUIRED"),
        bigquery.SchemaField('transaction_time',"TIMESTAMP",mode="REQUIRED"),
        ]

SOLD_TABLE = os.environ.get("SOLD_TABLE")
HERO_TAVERN_TABLE = os.environ.get("HERO_TAVERN_TABLE")

def create_bq_table(tableid,tableschema):
    client = bigquery.Client()
    table = bigquery.Table(tableid,schema=tableschema)
    table = client.create_table(table,exists_ok=True)
    print(f"Created table: {tableid}")

def delete_bq_table(tableid):
    client = bigquery.Client()
    client.delete_table(tableid, not_found_ok=True)
    print(f"Deleted table: {tableid}")

def write_hero(user_addr,_id,price,txn_hash,txn_time,tableid):
    client = bigquery.Client()
    table = client.get_table(tableid)
    rows_to_insert = [
            {
                "user_address":user_addr,
                "id":_id,
                "price":price,
                "transaction_hash":txn_hash,
                "transaction_time":txn_time.replace('/','-').replace(',','')
                }
            ]
    errors = client.insert_rows_json(table, rows_to_insert)
