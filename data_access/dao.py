""" Data Access Objects """
import json
from typing import Dict
from pymysql.err import Error
from data_access.db_client import MysqlClient


class AdvisorDAO:
    """ A Data Access Object
    that read and write personalized itinerary data.
     """

    def __init__(self, db_client: MysqlClient):
        self.db_client = db_client

    def get_member_body_index_data(self, request_id: str) -> Dict:

        sql_text = "select * from member_body_index_request where request_id=%s;"

        try:
            res, _ = self.db_client.exec_sql(sql_text, (request_id,))
            if res:
                return res[0]
        except Error as e:
            print(f"An error occurred during execution sql: {e}")

    def write_member_body_index_data(self, request_data: Dict) -> bool:
        column_holder = ", ".join(request_data.keys())
        request_column = f"({column_holder})"
        arg_holder = ", ".join(["%s"] * len(request_data.keys()))
        request_value = f"values({arg_holder});"

        sql_text = " ".join(["insert into member_body_index_request", request_column, request_value])

        args = tuple(request_data.values())

        try:
            self.db_client.exec_sql(sql_text, args)
            # return itinerary_uuid
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False

    def delete_member_body_index_data(self, request_id: str) -> bool:
        sql_text = "delete from member_body_index_request where request_id=%s"

        try:
            self.db_client.exec_sql(sql_text, (request_id,))
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False

    def get_body_index_advice(self, request_id: str) -> Dict:

        sql_text = "select * from member_body_index_advice_response where request_id=%s;"

        try:
            res, _ = self.db_client.exec_sql(sql_text, (request_id,))
            if res:
                return res[0]
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            raise Error

    def write_body_index_advice(self, request_id: str, response_json: Dict) -> bool:
        sql_text = "insert into member_body_index_advice_response (request_id, response_json) values(%s, %s);"
        args = (request_id, json.dumps(response_json))

        try:
            self.db_client.exec_sql(sql_text, args)
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False

    def delete_body_index_advice(self, request_id: str) -> bool:
        sql_text = "delete from member_body_index_advice_response where request_id=%s"

        try:
            self.db_client.exec_sql(sql_text, (request_id,))
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False
