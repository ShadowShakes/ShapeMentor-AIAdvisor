""" Data Access Objects """
import json
from typing import Dict
from pymysql.err import Error
from data_access.db_client import MysqlClient
from sqlalchemy.sql import text


class AdvisorDAO:
    """ A Data Access Object
    that read and write personalized itinerary data.
     """

    def __init__(self, db_client: MysqlClient):
        self.db_client = db_client

    def get_member_body_index_data(self, request_id: str) -> Dict:
        sql_text = text(f"SELECT * FROM member_body_index_request WHERE request_id = '{request_id}'")

        try:
            res, _ = self.db_client.exec_sql(sql_text)
            if res:
                row_dict = {
                    'request_id': res[0][0],
                    'name': res[0][1],
                    'track_data': res[0][2]
                }
                return row_dict

        except Error as e:
            print(f"An error occurred during execution sql: {e}")

    def write_member_body_index_data(self, request_data: Dict) -> bool:
        keys = list(request_data.keys())
        values = tuple(request_data.values())
        columns = ", ".join(keys)
        placeholders = ", ".join([":{}".format(key) for key in keys])

        sql_text = text(f"INSERT INTO member_body_index_request ({columns}) VALUES ({placeholders})")

        try:
            self.db_client.exec_sql(sql_text, dict(zip(keys, values)))
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False

    def delete_member_body_index_data(self, request_id: str) -> bool:
        sql_text = text("delete from member_body_index_request where request_id = :request_id")

        try:
            self.db_client.exec_sql(sql_text, {'request_id': request_id})
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False

    def get_body_index_advice(self, request_id: str) -> Dict:
        sql_text = text(f"SELECT * FROM member_body_index_advice_response WHERE request_id = '{request_id}'")

        try:
            res = self.db_client.exec_sql(sql_text, {'request_id': request_id})
            if res:
                row_dict = {
                    'request_id': res[0][0][0],
                    'response_json': res[0][0][1]
                }
                return row_dict
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            raise Error

    def write_body_index_advice(self, request_id: str, response_json: Dict) -> bool:
        sql_text = text("INSERT INTO member_body_index_advice_response (request_id, response_json) VALUES (:request_id, :response_json)")

        try:
            self.db_client.exec_sql(sql_text, {'request_id': request_id, 'response_json': json.dumps(response_json)})
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False

    def delete_body_index_advice(self, request_id: str) -> bool:
        sql_text = text("DELETE FROM member_body_index_advice_response WHERE request_id = :request_id")

        try:
            self.db_client.exec_sql(sql_text, {'request_id': request_id})
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False
