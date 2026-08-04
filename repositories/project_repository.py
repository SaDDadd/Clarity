from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, update, delete
from models.project import ProjectModel
from models.project_members import ProjectMemberModel
from core.exceptions import NotFoundException 

class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None: # Инициализация с подключением к БД
        self.session = session

    async def get_projects_by_admin(self, admin_id: int) -> list[ProjectModel]: # Получить все проекты 
        # админа
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.admin_id == admin_id))
        tasks = result.scalars().all()
        return tasks 
 
    async def update_project_description(self, new_description: str, project_id: int) -> bool: 
        # Обновить описание проекта
        result = await self.get_project_by_id(project_id)
        if result:
            task = await self.session.execute(update(ProjectModel).values(project_description=new_description).where(ProjectModel.project_id == project_id))
            await self.session.commit()
            return True
        else:
            return False
        
    async def update_project_name(self, new_name: str, project_id: int) -> bool:
        # Обновить имя проекта 
        result = await self.get_project_by_id(project_id)
        if result:
            task = await self.session.execute(update(ProjectModel).values(project_name=new_name).where(ProjectModel.project_id == project_id))
            await self.session.commit()
            return True
        else:
            return False
        
    async def is_user_in_project(self, project_id: int, user_id: int) -> bool: # Проверить, состоит 
        # ли пользователь в проекте
        result = await self.session.execute(select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id, ProjectMemberModel.user_id == user_id))
        task = result.scalar_one_or_none()
        if task:
            return True
        else:
            return False

    async def create_project_with_admin(self, name: str, description: str, admin_id: int, 
                                  role: str) -> ProjectModel: # Создать проект и добавить 
                                                                # админа
        task = ProjectModel(project_name=name, project_description=description, admin_id=admin_id)
        self.session.add(task)
        await self.session.flush()
        member = ProjectMemberModel(project_id=task.project_id, user_id=admin_id, role_project='admin')
        self.session.add(member)
        await self.session.commit()
        return task

    async def get_user_role_in_project(self, project_id: int, user_id: int) -> str | None: # Получить 
        # роль пользователя в проекте
        result = await self.session.execute(select(ProjectMemberModel.role_project).where(ProjectMemberModel.project_id == project_id, ProjectMemberModel.user_id == user_id))
        task = result.scalar_one_or_none()
        return task

    async def get_project_by_id(self, project_id: int) -> ProjectModel | None: # Получить проект по ID
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.project_id == project_id))
        task = result.scalar_one_or_none()
        return task

    async def get_project_all_info(self, project_id: int) -> dict | None: # Получить 
        # всю информацию о проекте
        result = await self.get_project_by_id(project_id)
        if result is None:
            raise NotFoundException('Запрашиваемого проекта нет!')
        else:
            result_2 = await self.session.execute(select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id))
            task_2 = result_2.scalars().all()
            return {'project': result, 
                    'members': task_2}

    async def is_user_admin(self, project_id: int, user_id: int) -> bool:
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.project_id == project_id, ProjectModel.admin_id == user_id))
        task = result.scalar_one_or_none()
        if task is None:
            return False
        else:
            return True

    async def delete_project(self, project_id) -> bool:
        async with self.session.begin():
            _ = await self.session.execute(delete(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id))
            result = await self.session.execute(delete(ProjectModel).where(ProjectModel.project_id == project_id))
            deleted_count = result.rowcount
        if deleted_count == 0:
            return False
        return True

    async def add_user(self, project_id, user_id) -> bool:
        if project_id is None or user_id is None:
            raise 
        else:
            task = ProjectMemberModel(project_id=project_id, user_id=user_id, role_project='member')
            self.session.add(task)
            await self.session.commit()
            return True