from flask import session
from functools import wraps


def check_log_in(func: object) -> object:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return 'You are not logged in'
    return wrapper
