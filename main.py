import datetime
import bcrypt
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from decorators.decorators import log
from models.user import User
from models.project import Project
from models.task import Task


@log
def create_user(user_repo: UserRepository) -> User: # Создание профиля
    print()
    print('Введите информацию о пользователе!')

    while True:
        username = input('Имя пользователя:')
        if user_repo.check_user_exists_by_username(username) is not None:
            print()
            print('Ошибка ввода: такое имя занято!')
        else:
            break

    while True:
        email = input('Email пользователя:')
        if user_repo.check_user_exists_by_email(email) is not None:
            print()
            print('Ошибка ввода: такой email занят!')
        else:
            break

    password = input('Пароль пользователя:')

    # Хэширование пароля
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    user_repo.create_user(username, email, password)

    user_now = user_repo.get_by_username(username)
    return user_now

@log
def create_project(project_repo: ProjectRepository, user_now: User) -> None: # Создание проекта
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

@log
def assign_task(project_repo: ProjectRepository, task_repo: TaskRepository,
                user_repo: UserRepository, project_now: Project, role_now: str) -> None: # Назначение задачи какому-то пользователю состоящему в проекте
    if role_now != 'admin':
        print('Только администратор проекта может назначать задачи.')
        return

    project_id = project_now.get_project_id()
    print(f'Назначение задачи в проекте "{project_now.get_project_name()}"')

    while True:
        try:
            task_id = int(input('Введите ID задачи: '))
        except ValueError:
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
        except ValueError:
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

@log
def change_status(task_repo: TaskRepository, user_now: User,
                  project_now: Project, role_now: str) -> None: # Изменить статус задачи
    project_id = project_now.get_project_id()
    print(f'Изменение статуса задачи в проекте "{project_now.get_project_name()}"')

    while True:
        try:
            task_id = int(input('Введите ID задачи: '))
        except ValueError:
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

def input_task_title() -> str: # Ввод названия задачи
    while True:
        title = input('Введите название задачи: ')
        if title:
            return title
        print('Название не может быть пустым.')

def input_task_description() -> str | None: # Ввод описания задачи (может быть None)
    answer = input('Хотите добавить описание? (Y/N): ').upper()
    if answer == 'Y':
        return input('Введите описание задачи: ')
    return None

def input_task_assigned_to(project_repo: ProjectRepository,
                           user_repo: UserRepository,
                           project_id: int) -> int | None: # Ввод ID исполнителя (может быть None)
    answer = input('Хотите назначить задачу на пользователя? (Y/N): ').upper()
    if answer != 'Y':
        return None

    while True:
        try:
            user_id = int(input('Введите ID пользователя: '))
        except ValueError:
            print('Ошибка ввода значения!')
            continue
        if not user_repo.check_user_exists(user_id):
            print('Пользователь с таким ID не найден.')
            continue
        if not project_repo.is_user_in_project(project_id, user_id):
            print('Этот пользователь не участвует в проекте.')
            continue
        return user_id

def input_task_deadline() -> datetime.date | None: # Ввод дедлайна (может быть None)
    answer = input('Хотите установить дедлайн? (Y/N): ').upper()
    if answer != 'Y':
        return None

    today = datetime.date.today()
    while True:
        date_str = input('Введите дату дедлайна (ГГГГ-ММ-ДД): ')
        try:
            deadline = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if deadline < today:
                print('Дедлайн не может быть в прошлом.')
                continue
            return deadline
        except ValueError:
            print('Неверный формат даты. Используйте ГГГГ-ММ-ДД.')

def create_task(project_repo: ProjectRepository, task_repo: TaskRepository,
                user_repo: UserRepository, project_now: Project, role: str) -> None: # Создание задач
    if role != 'admin':
        print('Только администратор проекта может создавать задачи!')
        return

    print(f'Создание задачи в проекте "{project_now.get_project_name()}" (ID {project_now.get_project_id()})')

    title = input_task_title()
    description = input_task_description()
    assigned_to = input_task_assigned_to(project_repo, user_repo, project_now.get_project_id())
    deadline = input_task_deadline()

    task_id = task_repo.create_task(
        title, description, 'pending',
        project_now.get_project_id(),
        assigned_to, deadline
    )
    if task_id:
        print(f'Задача успешно создана (ID {task_id}).')
    else:
        print('Ошибка при создании задачи.')

@log
def log_to_system(user_repo: UserRepository) -> User | None: # Вход в систему
    print()
    have_profile = input('У тебя есть профиль? (Y/N): ')

    if have_profile.upper() == 'Y':
        # Выбор способа входа
        while True:
            choice = input('Хотите войти в систему по имени пользователя(N) или по email(E)?: ')
            if choice.upper() in ('N', 'E'):
                break
            print('Неверный выбор, попробуйте снова.')

        # Цикл входа
        while True:
            print()
            if choice.upper() == 'E':
                email = input('Введите email: ')
                password = input('Введите пароль: ')
                if user_repo.check_user_exists_by_email(email) is None:
                    print('Данного email нету!')
                    continue
                if not user_repo.check_user_correct_password_by_email(email, password):
                    print('Неправильно введен пароль!')
                    continue
                print('Вы вошли в систему!')
                return user_repo.get_by_email(email)
            else:  # 'N'
                name = input('Введите имя пользователя: ')
                password = input('Введите пароль: ')
                if user_repo.check_user_exists_by_username(name) is None:
                    print('Данного имени не существует!')
                    continue
                if not user_repo.check_user_correct_password_by_username(name, password):
                    print('Неправильно введен пароль!')
                    continue
                print('Вы вошли в систему!')
                return user_repo.get_by_username(name)

    elif have_profile.upper() == 'N':
        return create_user(user_repo)
    else:
        print('Неверный ввод, попробуйте снова.')
        return log_to_system(user_repo)  # рекурсивно повторяем

@log
def log_to_project(project_repo: ProjectRepository, user_now: User) -> tuple[Project, str] | None: # Вход в проект
    user_id = user_now.get_user_id()
    while True:
        try:
            project_id = int(input('Введите ID проекта: '))
        except ValueError:
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

def menu_for_project() -> int | None: # Меню проекта
    print()
    print('Выберите что вы хотите делать с проектом!')
    print("1 - Создать задачу (только админ)")
    print("2 - Назначить задачу (только админ)")
    print("3 - Изменить статус задачи")
    print("4 - Выйти из проекта")
    try:
        choice = int(input('Введите ваш выбор:'))
        if choice not in (1, 2, 3, 4):
            print()
            print('Такого действия нет!')
            return None
        return choice
    except ValueError:
        print('Ошибка ввода')
        return None

def menu() -> int | None: # Меню выбора действий
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
        except ValueError:
            print('Ошибка ввода')

def main() -> None:
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
                project_role = log_to_project(project_repo, user_now)
                if project_role is None:
                    continue
                project_now, role_now = project_role
                while True:
                    action = menu_for_project()
                    if action == 1:
                        create_task(project_repo, task_repo, user_repo, project_now, role_now)
                    elif action == 2:
                        assign_task(project_repo, task_repo, user_repo, project_now, role_now)
                    elif action == 3:
                        change_status(task_repo, user_now, project_now, role_now)
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