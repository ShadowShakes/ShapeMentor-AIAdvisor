""" Define google cloud database clients. """

import pymysql
from pymysqlpool.pool import Pool
from typing import Dict, List, Tuple


class MysqlClient:
    """
    Mysql database client.
    """
    def __init__(self, host: str, username: str, password: str, database: str, pool_size=30):
        self.conn_pool = Pool(
            user=username,
            password=password,
            host=host,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            max_size=pool_size
        )

    def exec_sql(self, sql_text: str, *args, **kwargs) -> Tuple[List[Dict], int]:
        conn = self.conn_pool.get_conn()
        with conn.cursor() as cur:
            rows_affected = cur.execute(sql_text, *args, **kwargs)
            res = cur.fetchall()
        # release connection back to unused pool
        self.conn_pool.release(conn)
        return res, rows_affected
