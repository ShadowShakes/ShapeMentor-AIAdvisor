""" Data Access Objects """
import json
from typing import Dict
from pymysql.err import Error
from data_access.db_client import MysqlClient
from sqlalchemy.sql import text
from datetime import datetime


class AdvisorDAO:
    """ A Data Access Object
    that read and write personalized itinerary data.
     """

    def __init__(self, db_client: MysqlClient):
        self.db_client = db_client

    def get_user_body_metrics_data(self, user_email: str) -> Dict:
        sql_text = text(
            f"SELECT a.user_id, a.user_name, a.email, b.timestamp, c.metric_name, b.value, c.metric_unit FROM users AS a LEFT JOIN body_metrics AS b ON a.user_id = b.user_id LEFT JOIN body_metrics_lookup AS c ON b.metric_index = c.metric_index WHERE a.email = '{user_email}'")

        try:
            res, _ = self.db_client.exec_sql(sql_text)
            if res:
                track_data = {}
                for i, record in enumerate(res, start=1):
                    # Extracting record details
                    user_id, user_name, email, date, measure, value, unit = record
                    record_key = f"record{i}"

                    # Formatting date
                    formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")

                    # Adding or updating the record in track_data
                    if record_key not in track_data:
                        track_data[record_key] = {"date": formatted_date}
                    track_data[record_key][measure] = f"{value}{unit}" if unit != '%' else value / 100

                # Creating the final JSON structure
                final_json = {
                    "data": {
                        "user_id": user_id,
                        "user_name": user_name,
                        "user_email": email,
                        "advice_timestamp": datetime.utcnow().isoformat(),
                        "track_data": track_data
                    }
                }

                # Converting to JSON string for display
                json.dumps(final_json)
                return final_json

        except Error as e:
            print(f"An error occurred during execution sql: {e}")

    def get_current_body_metrics_advice_data(self, user_email: str) -> Dict:
        sql_text = text(f"SELECT * FROM ai_advice WHERE user_email = '{user_email}' ORDER BY advice_timestamp DESC LIMIT 1")

        try:
            res = self.db_client.exec_sql(sql_text, {'user_email': user_email})
            if res:
                return res[0][-1][-1]
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            raise Error

    def get_past_body_metrics_advice_data(self, user_email: str) -> Dict:
        sql_text = text(f"SELECT * FROM ai_advice WHERE user_email = '{user_email}' ORDER BY advice_timestamp DESC LIMIT 1 OFFSET 1")

        try:
            res = self.db_client.exec_sql(sql_text, {'user_email': user_email})
            if res:
                return res[0][-1][-1]
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            raise Error

    def write_body_metrics_advice_data(self, user_id: str, user_email: str, advice_timestamp: str, gpt_advice: Dict) -> bool:
        sql_text = text("INSERT INTO ai_advice (user_id, user_email, advice_timestamp, gpt_advice) VALUES (:user_id, :user_email, :advice_timestamp, :gpt_advice)")

        try:
            self.db_client.exec_sql(sql_text, {
                'user_id': user_id,
                'user_email': user_email,
                'advice_timestamp': advice_timestamp,
                'gpt_advice': json.dumps(gpt_advice)})
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False

    def delete_body_metrics_advice_data(self, user_email: str) -> bool:
        sql_text = text("DELETE FROM ai_advice WHERE user_email = :user_email")

        try:
            self.db_client.exec_sql(sql_text, {'request_id': user_email})
            return True
        except Error as e:
            print(f"An error occurred during execution sql: {e}")
            return False
