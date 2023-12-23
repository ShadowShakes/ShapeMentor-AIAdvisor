"""Support methods for application"""
import json
import os.path
import uuid
from typing import Dict
import cProfile
import pstats

import time
from jsonschema import validate, ValidationError


def get_root_path():
    return __file__.split('/utils.py', maxsplit=1)[0]


def transform_body_index_request_payload(user_email: str, payload: Dict) -> Dict or None:
    data = payload['data']
    data['user_email'] = user_email
    data['track_data'] = json.dumps(data['track_data'])
    return data


def generate_request_id() -> str:
    return str(uuid.uuid4())


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.6f} seconds")

        return result

    return wrapper
