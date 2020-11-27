import time
import traceback
from django.core.exceptions import ValidationError
from rest_framework import serializers


def basic_exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            from disturbance.components.main.utils import handle_validation_error
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
    return wrapper


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed