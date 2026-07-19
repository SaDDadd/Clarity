from functools import wraps
from typing import Callable
import time
import inspect

def log(func: Callable): # Возращает время работы функций и методов классов
    @wraps(func) # Для сохранения имени передаваемой функции func
    def wrapper(*args, **kwargs):
        if args and hasattr(args[0], '__class__'): 
            # Если в первом элементе идет self, 
            # значит это метод класса, иначе это обычная функция
            caller = f'{args[0].__class__.__name__}.{func.__name__}'
        else:
            caller = f'{func.__name__}'
        arg = args
        display_kwargs = kwargs.copy() 
        for i in display_kwargs:
            if i in ('password', 'hash'): # Если мы передаем пароли или хэш, 
                # то надо их спрятать 
                display_kwargs[i] = '***'
        print(f'Вызов {caller} с аргументами: {arg}, {display_kwargs}')
        start = time.time()
        try:
            res = func(*args, **kwargs)
            end = time.time()
            print(f'Время выполнения {end - start}, {res}')
            return res
        except Exception as error:
            end = time.time()
            print(f'Ошибка {error}, время {end - start}')
            raise # Пробрасываем ошибку
    return wrapper