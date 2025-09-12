import os
import psycopg2


DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),  # name of your postgres container in Docker Compose
    "port": os.environ.get("DB_PORT")
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


class PostgresConnection:
    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.conn = get_conn()
        self.cur = self.conn.cursor()
        return self.cur  # return the cursor for use in the with block

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()  # commit if no exception
        else:
            self.conn.rollback()  # rollback if exception occurred
        self.cur.close()
        self.conn.close()
