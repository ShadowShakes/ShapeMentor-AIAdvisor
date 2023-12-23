import time
import config
import utils
from flask import Flask, request, jsonify, Response
from datetime import datetime
from data_access.db_client import MysqlClient
from data_access.dao import AdvisorDAO
from service.ai_advisor import AIAdvisor
from exceptions import RequestNotFoundError, BadRequestError, InternalError

app = Flask(__name__)

mysql_client = MysqlClient(config.DB_HOST, config.DB_USERNAME,
                           config.DB_PW, config.DB_NAME)
advice_dao = AdvisorDAO(mysql_client)
ai_advisor = AIAdvisor()


@app.route('/')
def hello_world():  # put application's code here
    return 'Welcome to ShapeMentor AI Mentor!'


@app.route('/health', methods=['GET'])
def check_health():
    return {'msg': 'server is healthy!', 'datetime': datetime.now()}


@app.route('/ai_advisor/<user_email>/generate_advice', methods=['POST'])
def post_user_body_metrics_ai_generation(user_email: str):
    start_time = time.time()
    try:
        body_metrics_request_data = advice_dao.get_user_body_metrics_data(user_email)

        if body_metrics_request_data is None:
            raise RequestNotFoundError

        use_gpt4 = request.args.get('use_gpt4', default='false') == 'true'

        user_name = body_metrics_request_data["data"]["user_name"]
        user_id = body_metrics_request_data["data"]["user_id"]
        user_email = body_metrics_request_data["data"]["user_email"]
        advice_timestamp = body_metrics_request_data["data"]["advice_timestamp"]
        track_data = body_metrics_request_data["data"]["track_data"]

        transformed_json = {
            "user_name": user_name,  # Use the extracted user_name
            "track_data": list(track_data.values())  # Convert track_data to a list
        }

        personalized_advice = ai_advisor.get_body_metrics_advice(transformed_json, use_gpt4)

        if not advice_dao.write_body_metrics_advice_data(user_id, user_email, advice_timestamp, personalized_advice):
            raise InternalError

        return success_rsp({'user_email': user_email, 'response_data': personalized_advice,
                            'execution_time': time.time() - start_time, 'use_gpt4_for_plan': use_gpt4})
    except Exception as e:
        if isinstance(e, RequestNotFoundError):
            raise RequestNotFoundError
        print(f'unexpected exceptions: {e}')
        raise InternalError
    finally:
        print("request completed in {.2f} seconds", time.time() - start_time)


@app.route('/ai_advisor/<user_email>/get_current_advice', methods=['GET'])
def get_user_body_metrics_ai_response_current(user_email: str):
    try:
        advice_response = advice_dao.get_current_body_metrics_advice_data(user_email)

        if advice_response is None:
            raise RequestNotFoundError

        return success_rsp({"response_data": advice_response})
    except Exception as e:
        if isinstance(e, RequestNotFoundError):
            raise RequestNotFoundError
        print(f'unexpected exceptions: {e}')
        raise InternalError


@app.route('/ai_advisor/<user_email>/get_past_advice', methods=['GET'])
def get_user_body_metrics_ai_response_past(user_email: str):
    try:
        advice_response = advice_dao.get_past_body_metrics_advice_data(user_email)

        if advice_response is None:
            raise RequestNotFoundError

        return success_rsp({"response_data": advice_response})
    except Exception as e:
        if isinstance(e, RequestNotFoundError):
            raise RequestNotFoundError
        print(f'unexpected exceptions: {e}')
        raise InternalError


@app.errorhandler(RequestNotFoundError)
@app.errorhandler(BadRequestError)
@app.errorhandler(InternalError)
def handle_error(error):
    response = jsonify({'error': error.message, 'status_code': error.status_code})
    response.status_code = error.status_code
    return response


def success_rsp(data) -> Response:
    rsp = {'status_code': 200, 'data': data}
    return jsonify(rsp)


if __name__ == '__main__':
    app.run()
