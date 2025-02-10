from fastapi import FastAPI
from postgres_interaction import crt_engine, test_connection, is_postgres_table_exists, get_first_handle_trn, upd_rows_by_condition, get_all_categories
import os

from pydantic import BaseModel
from typing import Dict

from dotenv import load_dotenv
load_dotenv()


pg_conn_data = {
    'PG_USER': os.getenv('POSTGRES_USER'),
    'PG_PASS': os.getenv('POSTGRES_PASSWORD'),
    'PG_HOST': os.getenv('POSTGRES_HOST'),
    'PG_PORT': os.getenv('POSTGRES_PORT'),
    'PG_DB': os.getenv('POSTGRES_DATABASE')
}

SCHEMA = os.getenv('SCHEMA')
STG_TABLE = os.getenv('STG_TABLE')


app = FastAPI()

@app.get("/get_last_trn")
def get_last_trn():
    pg_engine = crt_engine(pg_conn_data)

    if test_connection(pg_engine) \
        and is_postgres_table_exists(pg_engine, STG_TABLE, SCHEMA):
        return get_first_handle_trn(pg_engine, STG_TABLE, SCHEMA)
    else:
        return None


@app.get("/get_categories")
def get_categories():
    pg_engine = crt_engine(pg_conn_data)

    if test_connection(pg_engine) \
        and is_postgres_table_exists(pg_engine, STG_TABLE, SCHEMA):
        return get_all_categories(pg_engine, STG_TABLE, SCHEMA)
    else:
        return None


class Item(BaseModel):
    set_dict: Dict[str, str]

@app.put("/update_trn/{trn_id}")
def update_trn(trn_id: str, item: Item):
    condition_dict = {
        'trn_id': trn_id
    }

    item = item.dict()

    pg_engine = crt_engine(pg_conn_data)

    

    if test_connection(pg_engine) \
        and is_postgres_table_exists(pg_engine, STG_TABLE, SCHEMA):
        resp = upd_rows_by_condition(pg_engine, STG_TABLE, SCHEMA, item['set_dict'], condition_dict)
    else:
        resp = None
    
    return resp

