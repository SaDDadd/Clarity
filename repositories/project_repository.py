from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.project import ProjectModel
from models.user import UserModel
from models.project_members import ProjectMemberModel
from models.project_invitations import ProjectInvitationModel
from models.task import TaskModel

class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_project_with_admin(self, name: str, description: str | None, admin_id: int) -> ProjectModel:
        """Создать проект и добавить админа."""
        task = ProjectModel(
            project_name=name,
            project_description=description,
            admin_id=admin_id,
        )
        self.session.add(task)
        await self.session.flush()
        member = ProjectMemberModel(
            project_id=task.project_id,
            user_id=admin_id,
            role_project="admin",
        )
        self.session.add(member)
        await self.session.commit()
        return task

    async def add_user(self, project_id: int, user_id_to_add: int) -> bool:
        """Добавить пользователя в проект."""
        task = ProjectMemberModel(
            project_id=project_id,
            user_id=user_id_to_add,
            role_project="member",
        )
        self.session.add(task)
        await self.session.commit()
        if task:
            return True
        else:
            return False

    async def get_projects_by_admin(self, admin_id: int) -> list[ProjectModel]:
        """Получить все проекты админа."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.admin_id == admin_id)
        )
        tasks = result.scalars().all()
        return tasks

    async def is_user_in_project(self, project_id: int, user_id: int) -> bool:
        """Проверить, состоит ли пользователь в проекте."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        task = result.scalar_one_or_none()
        if task:
            return True
        else:
            return False

    async def get_user_role_in_project(self, project_id: int, user_id: int) -> str | None:
        """Получить роль пользователя в проекте."""
        result = await self.session.execute(
            select(ProjectMemberModel.role_project).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        task = result.scalar_one_or_none()
        return task

    async def get_project_by_id(self, project_id: int) -> ProjectModel | None:
        """Получить проект по ID."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.project_id == project_id)
        )
        task = result.scalar_one_or_none()
        return task

    async def get_project_all_info(self, project_id: int) -> dict | None:
        """Получить всю информацию о проекте."""
        project_object = await self.get_project_by_id(project_id)
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id
            )
        )
        task_2 = result.scalars().all()
        return {"project": project_object, "members": task_2}

    async def reassign_admin(self, project_id: int, new_admin_id: int) -> bool:
        """Переназначить админа проекта."""
        result = await self.session.execute(
            update(ProjectModel)
            .where(ProjectModel.project_id == project_id)
            .values(admin_id=new_admin_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_admins_list(self, project_id: int) -> list[ProjectMemberModel]:
        """Получить всех администраторов проекта."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.role_project == "admin",
            )
        )
        return result.scalars().all()

    async def is_user_admin(self, project_id: int, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором проекта."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
                ProjectMemberModel.role_project == "admin",
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_user_projects(self, user_id: int) -> list[ProjectModel]:
        """Получить все проекты пользователя."""
        result = await self.session.execute(
            select(ProjectModel)
            .join(
                ProjectMemberModel,
                ProjectModel.project_id == ProjectMemberModel.project_id,
            )
            .where(ProjectMemberModel.user_id == user_id)
        )
        task = result.scalars().all()
        return task

    async def update_project_description(self, new_description: str, project_id: int) -> bool:
        """Обновить описание проекта."""
        result = await self.session.execute(
            update(ProjectModel)
            .values(project_description=new_description)
            .where(ProjectModel.project_id == project_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def update_project_name(self, new_name: str, project_id: int) -> bool:
        """Обновить имя проекта."""
        result = await self.session.execute(
            update(ProjectModel)
            .values(project_name=new_name)
            .where(ProjectModel.project_id == project_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def update_user_role(self, project_id: int, user_id: int, role: str) -> bool:
        """Обновить роль пользователя в проекте."""
        task = await self.session.execute(
            update(ProjectMemberModel)
            .values(role_project=role)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        await self.session.commit()
        return task.rowcount > 0

    async def delete_project_member(self, project_id: int, user_id: int) -> bool:
        """Удалить пользователя из проекта."""
        result = await self.session.execute(
            delete(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        delete_count = result.rowcount
        await self.session.commit()
        if delete_count == 0:
            return False
        else:
            return True

    async def delete_project(self, project_id: int) -> bool:
        """Удалить проект."""
        try:
            await self.session.execute(
                delete(ProjectMemberModel).where(
                    ProjectMemberModel.project_id == project_id
                )
            )
            await self.session.execute(
                delete(TaskModel).where(TaskModel.project_id == project_id)
            )
            await self.session.execute(
                delete(ProjectInvitationModel).where(
                    ProjectInvitationModel.project_id == project_id
                )
            )
            result = await self.session.execute(
                delete(ProjectModel).where(ProjectModel.project_id == project_id)
            )
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            print(f"ERROR deleting project {project_id}: {e}")
            await self.session.rollback()
            return False

    async def delete_user_from_project(self, project_id: int, user_id_to_del: int) -> bool:
        """Удалить пользователя из проекта."""
        result = await self.session.execute(
            delete(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id_to_del,
            )
        )
        delete_count = result.rowcount
        await self.session.commit()
        if delete_count == 0:
            return False
        else:
            return True

    async def get_number_admins(self, project_id: int) -> int:
        """Получить количество администраторов проекта."""
        result = await self.session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.role_project == "admin",
            )
        )
        return result.scalar() or 0

    async def automatically_assign_admin(self, project_id: int, user_id: int) -> int | None:
        """Автоматически назначить одного из пользователей проекта админом, 
        когда прошлы единственный админ удаляет профиль"""
        result = await self.session.execute(
            select(UserModel.user_id)
            .where(ProjectMemberModel.project_id == project_id, 
                   ProjectMemberModel.user_id != user_id)
            .order_by(ProjectMemberModel.joined_date, ProjectMemberModel.user_id)
            .limit(1))
        new_admin_id = result.scalar()
        if new_admin_id is None:
            return None
        await self.session.execute(
            update(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == new_admin_id,
            )
            .values(role_project='admin')
        )
        await self.session.commit()
        return new_admin_id

    async def get_number_members(self, project_id) -> int | None:
        """Получить количество участников(без админов) проекта."""
        result = await self.session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.role_project == 'member',
            )
        )
        return result.scalar() or 0