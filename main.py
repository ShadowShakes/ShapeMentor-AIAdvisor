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


@app.route('/ai_advisor/upload_request', methods=['POST'])
def post_member_body_index_upload_request():
    payload = request.json
    request_id = utils.generate_request_id()

    request_data = utils.transform_body_index_request_payload(request_id, payload)

    if request_data is None:
        raise BadRequestError

    try:
        if not advice_dao.write_member_body_index_data(request_data):
            raise InternalError

        return success_rsp({'request_id': request_id})

    except Exception as e:
        if isinstance(e, BadRequestError):
            raise BadRequestError
        print(f'unexpected exceptions: {e}')
        raise InternalError


@app.route('/ai_advisor/<request_id>/ai_generation', methods=['POST'])
def post_member_body_index_ai_generation(request_id: str):
    start_time = time.time()
    try:
        body_index_request_data = advice_dao.get_member_body_index_data(request_id)

        if body_index_request_data is None:
            raise RequestNotFoundError

        use_gpt4 = request.args.get('use_gpt4', default='false') == 'true'
        personalized_advice = ai_advisor.get_body_index_advice(body_index_request_data, use_gpt4)

        if not advice_dao.write_body_index_advice(request_id, personalized_advice):
            raise InternalError

        return success_rsp({'request_id': request_id, 'response_data': personalized_advice,
                            'execution_time': time.time() - start_time, 'use_gpt4_for_plan': use_gpt4})
    except Exception as e:
        if isinstance(e, RequestNotFoundError):
            raise RequestNotFoundError
        print(f'unexpected exceptions: {e}')
        raise InternalError
    finally:
        print("request completed in {.2f} seconds", time.time() - start_time)


@app.route('/ai_advisor/<request_id>', methods=['GET'])
def get_member_body_index_ai_response(request_id: str):
    try:
        advice_response = advice_dao.get_body_index_advice(request_id)

        if advice_response is None:
            raise RequestNotFoundError

        return success_rsp(advice_response)
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
