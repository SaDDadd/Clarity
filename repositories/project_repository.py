from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import ConflictException, LackOfInformationException, NotFoundException
from models.project import ProjectModel
from models.project_members import ProjectMemberModel
from models.project_invitations import ProjectInvitationModel
from models.task import TaskModel
from sqlalchemy import func 


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Создать проект и добавить админа
    async def create_project_with_admin(self, name: str, description: str, admin_id: int, role: str) -> ProjectModel:
        task = ProjectModel(
            project_name=name,
            project_description=description,
            admin_id=admin_id
        )
        self.session.add(task)
        await self.session.flush()
        member = ProjectMemberModel(
            project_id=task.project_id,
            user_id=admin_id,
            role_project='admin'
        )
        self.session.add(member)
        await self.session.commit()
        return task

    # Добавить пользователя в проект
    async def add_user(self, project_id: int, user_id_to_add: int) -> bool:
        task = ProjectMemberModel(
            project_id=project_id,
            user_id=user_id_to_add,
            role_project='member'
        )
        self.session.add(task)
        await self.session.commit()
        if task:
            return True
        else:
            return False

    # Получить все проекты админа
    async def get_projects_by_admin(self, admin_id: int) -> list[ProjectModel]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.admin_id == admin_id)
        )
        tasks = result.scalars().all()
        return tasks

    # Проверить, состоит ли пользователь в проекте
    async def is_user_in_project(self, project_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id
            )
        )
        task = result.scalar_one_or_none()
        if task:
            return True
        else:
            return False

    # Получить роль пользователя в проекте
    async def get_user_role_in_project(self, project_id: int, user_id: int) -> str | None:
        result = await self.session.execute(
            select(ProjectMemberModel.role_project).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id
            )
        )
        task = result.scalar_one_or_none()
        return task

    # Получить проект по ID
    async def get_project_by_id(self, project_id: int) -> ProjectModel | None:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.project_id == project_id)
        )
        task = result.scalar_one_or_none()
        return task

    # Получить всю информацию о проекте
    async def get_project_all_info(self, project_id: int) -> dict | None:
        project_object = await self.get_project_by_id(project_id)
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id
            )
        )
        task_2 = result.scalars().all()
        return {'project': project_object, 'members': task_2}

    # Переназначить админа проекта 
    async def reassign_admin(self, project_id: int, new_admin_id: int) -> bool:
        result = await self.session.execute(update(ProjectModel).where(ProjectModel.project_id == project_id).values(admin_id=new_admin_id))
        await self.session.commit()
        return result.rowcount > 0

    # Получить всех администраторов проекта
    async def get_admins_list(self, project_id: int) -> list[ProjectMemberModel]:
        result = await self.session.execute(select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id,ProjectMemberModel.role_project == 'admin'))
        return result.scalars().all()
    
    # Проверить, является ли пользователь администратором проекта
    async def is_user_admin(self, project_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
                ProjectMemberModel.role_project == 'admin'
            )
        )
        return result.scalar_one_or_none() is not None

    # Получить все проекты пользователя
    async def get_user_projects(self, user_id) -> list[ProjectModel]:
        result = await self.session.execute(
            select(ProjectModel)
            .join(ProjectMemberModel, ProjectModel.project_id == ProjectMemberModel.project_id)
            .where(ProjectMemberModel.user_id == user_id)
        )
        task = result.scalars().all()
        return task

    # Обновить описание проекта
    async def update_project_description(self, new_description: str, project_id: int) -> bool:
        result = await self.get_project_by_id(project_id)
        if result:
            await self.session.execute(
                update(ProjectModel)
                .values(project_description=new_description)
                .where(ProjectModel.project_id == project_id)
            )
            await self.session.commit()
            return True
        else:
            return False

    # Обновить имя проекта
    async def update_project_name(self, new_name: str, project_id: int) -> bool:
        result = await self.get_project_by_id(project_id)
        if result:
            await self.session.execute(
                update(ProjectModel)
                .values(project_name=new_name)
                .where(ProjectModel.project_id == project_id)
            )
            await self.session.commit()
            return True
        else:
            return False

    # Обновить роль пользователя в проекте
    async def update_user_role(self, project_id: int, user_id: int, role: str) -> bool:
        task = await self.session.execute(update(ProjectMemberModel).values(role_project=role).where(ProjectMemberModel.project_id == project_id, ProjectMemberModel.user_id == user_id))
        await self.session.commit()
        return task.rowcount > 0

    # Удалить пользователя из проекта
    async def delete_project_member(self, project_id: int, user_id: int) -> bool:
        result = await self.session.execute(delete(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id, ProjectMemberModel.user_id == user_id))
        delete_count = result.rowcount
        if delete_count == 0:
            return False
        else:
            return True

    # Удалить проект
    async def delete_project(self, project_id) -> bool:
        async with self.session.begin():
        # Удаляем связанные записи (если CASCADE не сработает)
            await self.session.execute(delete(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id))
            await self.session.execute(delete(TaskModel).where(TaskModel.project_id == project_id))
            await self.session.execute(delete(ProjectInvitationModel).where(ProjectInvitationModel.project_id == project_id))
            result = await self.session.execute(delete(ProjectModel).where(ProjectModel.project_id == project_id))
            return result.rowcount > 0

    # Удалить пользователя из проекта
    async def delete_user(self, project_id, user_id_to_del) -> bool:
        result = await self.session.execute(
            delete(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id_to_del
            )
        )
        delete_count = result.rowcount
        if delete_count == 0:
            return False
        else:
            return True

    async def get_number_admins(self, project_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.role_project == 'admin'
            )
        )
        return result.scalar() or 0