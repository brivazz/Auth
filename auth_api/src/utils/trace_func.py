from functools import wraps

from opentelemetry import trace


def traced(name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(func.__name__ if not name else name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
