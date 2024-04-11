from functools import wraps
from flask import request, jsonify
from app.src import app_config
import mysql.connector
import hashlib


def hash_password(password):
    # Konwertuj hasło na bajty (utf-8)
    password_bytes = password.encode('utf-8')

    # Użyj funkcji SHA-256 do zahashowania hasła
    hashed_password = hashlib.sha256(password_bytes).hexdigest()

    return hashed_password


def access_denied():
    return {'status': 'fail', 'message': 'no_session_token'}, 401


def admin_verify(admin_api_key: str):
    # To-Do: Implement verification via db
    if admin_api_key == 'test':
        return True
    else:
        return False


def verify(api_key: str):
    with mysql.connector.connect(**app_config.MYSQL_CONFIG) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute("SELECT count(api_key) AS number FROM users WHERE api_key = '"+api_key + "'")
            result = cursor.fetchall()

            if result[0][0] == 1:
                return True

            return False


def requires(*args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*wrapped_args, **wrapped_kwargs):
            query_params = request.args
            missing_params = [param for param in args if param not in query_params]
            if missing_params:
                return jsonify({"status": "fail", "message": "missing_required_parameters", "missing": missing_params}), 400
            return func(*wrapped_args, **wrapped_kwargs)
        return wrapper
    return decorator


def admin_auth(func):
    @wraps(func)
    def verify_key(*args, **kwargs):
        if request.args.get('session_token') and admin_verify(request.args.get('session_token')):
            return func(*args, **kwargs)
        else:
            return access_denied()
    return verify_key


def auth(func):
    @wraps(func)
    def verify_key(*args, **kwargs):
        if request.args.get('session_token') and verify(request.args.get('session_token')):
            return func(*args, **kwargs)
        else:
            return access_denied()
    return verify_key