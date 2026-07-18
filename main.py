import datetime
import bcrypt
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from models.task import Task

def create_user(user_repo): # Создание профиля
    print()
    print('Введите информацию о пользователе!')
    flag_stop = False
    while flag_stop == False:
        username = input('Имя пользователя:')
        if user_repo.check_user_exists_by_username(username) is not None:
            print()
            print('Ошибка ввода: такое имя занято!')
        else:
            flag_stop = True

    flag_stop = False 

    while flag_stop == False:
        email = input('Email пользователя:')
        if user_repo.check_user_exists_by_email(email) is not None:
            print()
            print('Ошибка ввода: такой email занят!')
        else:
            flag_stop = True
    password = input('Пароль пользователя:')

    # Хэширование пароля
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    user_repo.create_user(username, email, password)

    user_now = user_repo.get_by_username(username)
    return user_now 

def create_project(project_repo, user_now): # Создание проекта 
    print()
    print('Введите информацию о проекте!')
    name = input('Название проекта:')
    description = input('Описание проекта:')
    admin_id = user_now.get_user_id()
    if project_repo.create_project_with_admin(name, description, admin_id, 'admin') is None:
        print()
        print('При создании проекта произошла ошибка!')
    else:
        print()
        print('Проект создан!')

def assign_task(task_repo, project_repo, user_repo, user_now, project_now, role_now): # Назначение задачи какому-то пользователю состоящему в проекте
    if role_now != 'admin':
        print('Только администратор проекта может назначать задачи.')
        return

    project_id = project_now.get_project_id()
    print(f'Назначение задачи в проекте "{project_now.get_project_name()}"')

    while True:
        try:
            task_id = int(input('Введите ID задачи: '))
        except ValueError as error:
            print('Ошибка: введите число.')
            continue

        task = task_repo.get_task_by_id(task_id)
        if task is None:
            print('Задача с таким ID не найдена.')
            continue
        if task.get_project_id() != project_id:
            print('Эта задача не принадлежит текущему проекту.')
            continue
        break

    while True:
        try:
            user_id = int(input('Введите ID пользователя, которому назначить задачу: '))
        except ValueError as error:
            print('Ошибка: введите число.')
            continue
        if not user_repo.check_user_exists(user_id):
            print('Пользователь с таким ID не найден.')
            continue
        if not project_repo.is_user_in_project(project_id, user_id):
            print('Этот пользователь не участвует в проекте.')
            continue
        break

    affected = task_repo.assign_task(user_id, task_id)
    if affected:
        print('Задача успешно назначена.')
    else:
        print('Ошибка при назначении задачи.')

def change_status(project_repo, task_repo, user_now, user_repo, project_now, role_now): # Изменить статус задачи
    project_id = project_now.get_project_id()
    print(f'Изменение статуса задачи в проекте "{project_now.get_project_name()}"')

    while True:
        try:
            task_id = int(input('Введите ID задачи: '))
        except ValueError as error:
            print('Ошибка: введите число.')
            continue

        task = task_repo.get_task_by_id(task_id)
        if task is None:
            print('Задача с таким ID не найдена.')
            continue
        if task.get_project_id() != project_id:
            print('Эта задача не принадлежит текущему проекту.')
            continue
        break

    if role_now != 'admin' and task.get_assigned_to() != user_now.get_user_id():
        print('Вы не можете изменять статус этой задачи (только администратор или исполнитель).')
        return

    while True:
        status = input('Введите новый статус (pending/in_progress/completed):')
        if status not in ('pending', 'in_progress', 'completed'):
            print('Недопустимый статус.')
            continue
        break

    affected = task_repo.update_task_by_id(task_id, status)
    if affected:
        print('Статус обновлён.')
    else:
        print('Ошибка при обновлении статуса.')
    
def create_task(project_repo, task_repo, user_repo, user_now, project_now, role):
    if role != 'admin':
        print('Только администратор проекта может создавать задачи!')
        return

    print(f'Создание задачи в проекте "{project_now.get_project_name()}" (ID {project_now.get_project_id()})')

    title = input('Введите название задачи: ')
    while not title:
        print('Название не может быть пустым.')
        title = input('Введите название задачи: ')

    
    description = None
    answer = input('Хотите добавить описание? (Y/N): ').upper()
    if answer == 'Y':
        description = input('Введите описание задачи: ')

    assigned_to = None
    answer = input('Хотите назначить задачу на пользователя? (Y/N): ').upper()
    if answer == 'Y':
        while True:
            try:
                user_id = int(input('Введите ID пользователя: '))
            except ValueError as error:
                print('Ошибка ввода значения!')
                continue
            if not user_repo.check_user_exists(user_id):
                print('Пользователь с таким ID не найден.')
                continue
            if not project_repo.is_user_in_project(project_now.get_project_id(), user_id):
                print('Этот пользователь не участвует в проекте.')
                continue
            assigned_to = user_id
            break

    deadline = None
    answer = input('Хотите установить дедлайн? (Y/N): ').upper()
    if answer == 'Y':
        while True:
            date_str = input('Введите дату дедлайна (ГГГГ-ММ-ДД): ')
            try:
                deadline = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                if deadline < datetime.date.today():
                    print('Дедлайн не может быть в прошлом.')
                    continue
                break
            except ValueError as error:
                print('Неверный формат даты. Используйте ГГГГ-ММ-ДД.')

    task_id = task_repo.create_task(title, description, 'pending', project_now.get_project_id(), \
                                    assigned_to, deadline)
    if task_id:
        print(f'Задача успешно создана (ID {task_id}).')
    else:
        print('Ошибка при создании задачи.')
    
def log_to_system(user_repo): # Вход в систему
    user_now = None

    print()
    have_profile= input('У тебя есть профиль? (Y/N): ')
    if have_profile.upper() == 'Y':
        flag_stop = False
        choice = input('Хотите войти в систему по имени пользователя(N) или по email(E)?:')
        while flag_stop == False:
            if choice.upper() == 'E':
                while True:
                    print()
                    email = input('Введите email: ')
                    password = input('Введите пароль: ')

                    if user_repo.check_user_exists_by_email(email) is None:
                        print()
                        print('Данного email нету!')
                    elif user_repo.check_user_correct_password_by_email(email, password) is False:
                        print()
                        print('Неправильно введен пароль!')
                    else:
                        print()
                        print('Вы вошли в систему!')
                        flag_stop = True
                        user_now = user_repo.get_by_email(email)
                        break
            elif choice.upper() == 'N':
                while True:
                    print()
                    name = input('Введите имя пользователя: ')
                    password = input('Ведите пароль: ')
                    
                    if user_repo.check_user_exists_by_username(name) is None:
                        print()
                        print('Данного имени не существует!')
                    elif user_repo.check_user_correct_password_by_username(name, password) is False:
                        print()
                        print('Неправильно введен пароль!')
                    else:
                        print()
                        print('Вы вошли в систему!')
                        flag_stop = True
                        user_now = user_repo.get_by_username(name)
                        break
            else:
                print()
                choice = input('Хотите войти в систему по имени пользователя(N) или по email(E)?:')
    elif have_profile.upper() == 'N':
        user_now = create_user(user_repo)

    return user_now

def log_to_project(project_repo, user_now):
    user_id = user_now.get_user_id()
    while True:
        try:
            project_id = int(input('Введите ID проекта: '))
        except ValueError as error:
            print('Ошибка ввода ID')
            continue

        project = project_repo.get_project_by_id(project_id)
        if project is None:
            print('Проекта с таким ID не существует!')
            continue

        role = project_repo.get_user_role_in_project(project_id, user_id)
        if role is None:
            print('Вы не являетесь участником этого проекта!')
            continue

        print(f'Вы вошли в проект "{project.get_project_name()}" с ролью "{role}".')
        return project, role
        
def menu_for_project():
    print()
    print('Выберите что вы хотите делать с проектом!')
    print('1 - Войти в проект')
    print('2 - Создать задачу в проекте (только для админов)')
    print('3 - Назначить задачу в проекте (только для админов)')
    print('4 - Изменить статус задачи')
    try:
        choice = int(input('Введите ваш выбор:'))
        if choice not in (1, 2, 3, 4):
            print()
            print('Такого действия нет!')
        else:
            return choice
    except ValueError as error:
        print(f'Ошибка ввода {error}')

def menu():
    while True:
        print()
        print('Выберите действие, которое хотите выполнить!')
        print('1 - Создать проект')
        print('2 - Работа с проектом')
        print('3 - Закончить работу')
        try:
            choice = int(input('Введите ваш выбор:'))
            if choice not in (1, 2, 3):
                print()
                print('Такого действия нет!')
            else:
                return choice
        except ValueError as error:
            print(f'Ошибка ввода {error}')

def main():
    user_repo = UserRepository()
    task_repo = TaskRepository()
    project_repo = ProjectRepository()

    user_now = log_to_system(user_repo)

    if user_now is None:
        print('Работа закончена!')
        return

    while True:
        choice = menu()
        match choice:
            case 1:
                create_project(project_repo, user_now)
            case 2:
                project, role = log_to_project(project_repo, user_now)
                if project is None:
                    continue
                while True:
                    print()
                    print('Действия с проектом:')
                    print('1 - Создать задачу (только админ)')
                    print('2 - Назначить задачу (только админ)')
                    print('3 - Изменить статус задачи')
                    print('4 - Выйти из проекта')
                    try:
                        action = int(input('Ваш выбор: '))
                    except ValueError:
                        print('Ошибка ввода.')
                        continue
                    if action == 1:
                        create_task(project_repo, task_repo, user_repo, user_now, project, role)
                    elif action == 2:
                        assign_task(project_repo, task_repo, user_repo, user_now, project, role)
                    elif action == 3:
                        change_status(project_repo, task_repo, user_now, project, role)
                    elif action == 4:
                        print('Выход из проекта.')
                        break
                    else:
                        print('Неверный выбор.')
            case 3:
                print('Работа закончена!')
                return

if __name__ == '__main__':
    main()