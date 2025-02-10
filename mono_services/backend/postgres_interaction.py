# %%
from sqlalchemy import create_engine, text, inspect


# %%
def crt_engine(pg_conn_data):
    """
    Функція створює connection у Postgres DB

    Параметри:
        - postgres credentials (str)
    
    Повертає:
        - sqlalchemy.engine.base.Engine - conn
    """
    # db_connection_str = f'postgresql://{pg_conn_data['PG_USER']}:{pg_conn_data['PG_PASS']}@{pg_conn_data['PG_HOST']}:{pg_conn_data['PG_PORT']}/{pg_conn_data['PG_DB']}'
    db_connection_str = f"postgresql://{pg_conn_data['PG_USER']}:{pg_conn_data['PG_PASS']}@{pg_conn_data['PG_HOST']}:{pg_conn_data['PG_PORT']}/{pg_conn_data['PG_DB']}"

    
    try:
        engine = create_engine(db_connection_str)
        return engine
    except Exception as e:
        print(f"ERROR: {e}")


# %%
def test_connection(engine):
    """
    Функція перевіряє підключення до engine

    Параметри:
        - engine (sqlalchemy.engine.base.Engine) - conn до postgres DB
    
    Повертає:
        - Bool - булеве значення успішного підʼєднання до postgres DB
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("Connection to Postgres DB successful!")
                return True
            else:
                print("Connection to Postgres DB failed.")
                return False
    except Exception as e:
        print(f"Connection error: {e}")


# %%
def is_postgres_table_exists(engine, tbl_name, schema):
    """
    Функція перевіряє чи існує таблиця у Postgres DB

    Параметри:
        - engine - Postgres DB engine
        - tbl_name (str) - назва таблиці postgres
        - schema (str) - назва схеми postgres
    
    Повертає:
        - Bool - маркер наявності таблиці у схемі Postgres DB
    """
    inspector = inspect(engine)

    if tbl_name in inspector.get_table_names(schema=schema):
        # print(f"Таблиця '{tbl_name}' існує.")
        return True
    else:
        # print(f"Таблиця '{tbl_name}' не знайдена.")
        return False


# %%
def run_query(engine, query, commit_marker=False):
    """
    Функція запускає Query у БД

    Параметри:
        - engine - Postgres DB engine
        - query (str) - запит
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            if commit_marker:
                connection.commit()
            print('Query runned Successfull.')
            return result
    except Exception as e:
        print(f"Query Error. ERROR: {e}")


# %%
def get_first_handle_trn(engine, stg_tbl_name, stg_schema):
    query = f"""
        SELECT
            trn_id
            , TO_CHAR(ts, 'YYYY-MM-DD HH24:MI') AS dt
            --, TO_CHAR(amount, 'FM999999.00') AS amount
            , amount
            , bank_description
            , mcc_group_description
            , mcc_short_description
        FROM {stg_schema}.{stg_tbl_name}
        WHERE handle_marker = 'true'
        ORDER BY trn_unix
        LIMIT 1
    """
    res = run_query(engine, query)
    try:
        res = res.mappings().first()
        transaction_dict = dict(res)
        return transaction_dict
    except Exception as e:
        print('0 rows returned')
        print('Exception - ', e)
        return {}


# %%
def get_all_categories(engine, stg_tbl_name, stg_schema):
    query = f"""
        SELECT category
        FROM mono_data.stg_transactions
        GROUP BY category
        ORDER BY COUNT(*) DESC
    """
    res = run_query(engine, query)
    result_list = [dict(row)['category'] for row in res.mappings()]
    return result_list
    # try:
    #     res = res.mappings().first()
    #     transaction_dict = dict(res)
    #     return transaction_dict
    # except Exception as e:
    #     print('0 rows returned')
    #     print('Exception - ', e)
    #     return {}


# %%
def upd_rows_by_condition(engine, stg_tbl_name, stg_schema, set_dict, condition_dict):
    set_str = ", ".join([f"{k} = '{v}'" for k, v in set_dict.items()])
    condition_str = " AND ".join([f"{k} = '{v}'" for k, v in condition_dict.items()])

    query = f"""
        UPDATE {stg_schema}.{stg_tbl_name}
        SET
            {set_str}
        WHERE
            {condition_str}
    """
    resp = run_query(engine, query, True)
    print(resp)
    return resp


# %%