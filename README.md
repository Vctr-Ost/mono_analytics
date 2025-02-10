.env files should be in:

- ./mono_postgres/.env

    POSTGRES_USER= (user_name postgres)
    POSTGRES_PASSWORD= (user_pass postgres)
    POSTGRES_DB= (db_name postgres)

- ./mono_project/dags/.env
    AIRFLOW_UID= (default 501)
    ACCOUNT_ID= (account_id monobank)
    X_TOKEN= (token monobank)

    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_HOST=
    POSTGRES_PORT=
    POSTGRES_DATABASE=

    SCHEMA_FOR_DATA= (schema_name in postgres for monobank data)
    TABLE_FOR_ROW_DATA= (table_name in postgres for monobank row data)
    TABLE_FOR_MCC_EN= (table_name in postgres for EN mcc codes)
    TABLE_FOR_MCC_UA= (table_name in postgres for UA mcc codes)
    TABLE_FOR_MCC_HANDLING_DATA= (table_name in postgres for mcc handling file)

- ./mono_services/backend/.env
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_HOST=
    POSTGRES_PORT=
    POSTGRES_DATABASE=

    SCHEMA= (schema_name in postgres for monobank data)
    STG_TABLE= (table_name in postgres for monobank stg data)

- ./mono_services/telegram_bot/.env
    ALLOWED_USER_ID= (user_id - owner of bot)
