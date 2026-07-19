from functools import wraps
from typing import Callable

def log(func: Callable): 
    @wraps(func) # Для сохранения имени передаваемой функции func
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if args == 'self': 
            # Если в первым элементом идет self, 
            # значит это метод класса, иначе это обычная функция
            name = args[0].__class__.__name__
        else:
            name = func.__name__
        arg = args
        kwarg = kwargs 
        for i in kwarg:
            if i in ('password', 'hash'):
                i = '***'
        print(f'Вызов {name}.{name} с аргументами: {arg}')

        return 
    return wrapper