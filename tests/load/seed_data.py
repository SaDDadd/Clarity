import asyncio
import uuid
import csv
import random
import datetime
import os

os.environ['ENV'] = 'test'

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings
from core.security import hash_password
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from schemas.task import TaskCreate

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with async_session() as session:
        user_repo = UserRepository(session)
        project_repo = ProjectRepository(session)
        task_repo = TaskRepository(session)

        users = []
        for i in range(50):
            username = f'{uuid.uuid4().hex[:10]}'
            email = f'{uuid.uuid4().hex[:8]}@mail.ru'
            hashed_password = hash_password('qwertyui')
            user = await user_repo.create_user(username, email, hashed_password)
            users.append(user)

        with open('tests/load/users.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password'])
            for user in users:
                writer.writerow([user.username, 'qwertyui'])
            
        projects = []
        for _ in range(50):
            admin_id = random.choice(users)
            project = await project_repo.create_project_with_admin(name=f'Load project {uuid.uuid4().hex[:10]}', \
                                                                   description=f'Description {uuid.uuid4().hex[:10]}', \
                                                                    admin_id=admin_id)
            projects.append(project)

        for project in projects:
            potential = [user for user in users if user.user_id != project.admin_id]
            num_member = random.randint(3, min(10, len(potential)))
            selected = random.sample(potential, num_member)
            for user in selected:
                await project_repo.add_user(project.project_id, user.user_id)

        for project in projects:
            member_info = await project_repo.get_project_all_info(project.project_id)
            member_ids = [user.user_id for user in member_info['members']]
            if not member_ids:
                continue
            for _ in range(10):
                assignee = random.choice(member_ids)
                deadline = datetime.date.today() + datetime.timedelta(days=random.randint(1, 30))
                task_data = TaskCreate(title=f'Task {uuid.uuid4().hex[:30]}', \
                                       task_description=f'Description {uuid.uuid4().hex[:30]}', \
                                        deadline=deadline, assigned_to=assignee)
                await task_repo.create_task(project.project_id, task_data)

        print('Данные для начального заполнения успешно созданы!')

if __name__ == '__main__':
    asyncio.run(seed)