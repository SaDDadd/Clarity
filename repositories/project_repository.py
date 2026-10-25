from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.project import ProjectModel
from models.task_comments import TaskCommentsModel
from models.project_members import ProjectMemberModel
from models.project_invitations import ProjectInvitationModel
from models.task import TaskModel

class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_project_with_admin(self, name: str, description: str | None, admin_id: int) -> ProjectModel:
        """Создаёт проект и назначает создателя владельцем (role='admin')."""
        project = ProjectModel(
            project_name=name,
            project_description=description,
            admin_id=admin_id
        )
        self.session.add(project)
        await self.session.flush()
        member = ProjectMemberModel(
            project_id=project.project_id,
            user_id=admin_id,
            role_project="admin"
        )
        self.session.add(member)
        await self.session.flush()
        return project

    async def add_user(self, project_id: int, user_id_to_add: int) -> bool:
        """Добавить пользователя в проект."""
        member = ProjectMemberModel(
            project_id=project_id,
            user_id=user_id_to_add,
            role_project="member"
        )
        self.session.add(member)
        await self.session.flush()
        return member is not None

    async def get_managed_projects(self, admin_id: int) -> list[ProjectModel]:
        """Проекты, где пользователь - владелец или администратор."""
        result = await self.session.execute(
            select(ProjectModel)
            .join(ProjectMemberModel)
            .where(
                ProjectMemberModel.user_id == admin_id,
                ProjectMemberModel.role_project.in_(['admin', 'curator'])
            )
        )
        return result.scalars().all()

    async def get_projects_by_creator(self, admin_id: int) -> list[ProjectModel]:
        """Проекты, где пользователь именно владелец."""
        result = await self.session.execute(
            select(ProjectModel)
            .join(ProjectMemberModel)
            .where(
                ProjectMemberModel.user_id == admin_id,
                ProjectMemberModel.role_project == 'admin'
            )
        )
        return result.scalars().all()

    async def is_user_in_project(self, project_id: int, user_id: int) -> bool:
        """Проверка есть ли пользователь в проекте."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_user_role_in_project(self, project_id: int, user_id: int) -> str | None:
        """Получить роль пользователя в проекте."""
        result = await self.session.execute(
            select(ProjectMemberModel.role_project).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_project_by_id(self, project_id: int) -> ProjectModel | None:
        """Получить проект по ID."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_project_all_info(self, project_id: int) -> dict:
        """Получить всю информацию проекта."""
        project_object = await self.get_project_by_id(project_id)
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id
            )
        )
        return {"project": project_object, "members": result.scalars().all()}

    async def reassign_admin(self, project_id: int, new_admin_id: int) -> bool:
        """Передаёт владение проектом."""
        old_admin = await self.get_project_by_id(project_id)
        if old_admin is None:
            return False
        if old_admin.admin_id == new_admin_id:
            return False
        result_project = await self.session.execute(
            update(ProjectModel)
            .where(ProjectModel.project_id == project_id)
            .values(admin_id=new_admin_id)
        )
        down_role = await self.session.execute(
            update(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == old_admin.admin_id,
            )
            .values(role_project='curator')
        )
        result_member = await self.session.execute(
            update(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == new_admin_id,
            )
            .values(role_project='admin')
        )
        await self.session.flush()
        return result_member.rowcount > 0 and result_project.rowcount > 0 and down_role.rowcount == 1

    async def automatically_assign_admin(self, project_id: int, leaving_user_id: int) -> int | None:
        """Подбирает нового владельца при уходе текущего."""
        result = await self.session.execute(
            select(ProjectMemberModel.user_id)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id != leaving_user_id,
                ProjectMemberModel.role_project == 'curator'
            )
            .order_by(ProjectMemberModel.joined_date, ProjectMemberModel.user_id)
            .limit(1)
        )
        new_admin_id = result.scalar()
        if new_admin_id is None:
            result = await self.session.execute(
                select(ProjectMemberModel.user_id)
                .where(
                    ProjectMemberModel.project_id == project_id,
                    ProjectMemberModel.user_id != leaving_user_id,
                    ProjectMemberModel.role_project == 'member'
                )
                .order_by(ProjectMemberModel.joined_date, ProjectMemberModel.user_id)
                .limit(1)
            )
            new_admin_id = result.scalar()
        if new_admin_id is None:
            return None
        await self.session.execute(
            update(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == new_admin_id
            )
            .values(role_project='admin')
        )
        await self.session.execute(
            update(ProjectModel)
            .where(ProjectModel.project_id == project_id)
            .values(admin_id=new_admin_id)
        )
        await self.session.flush()
        return new_admin_id

    async def get_curators_list(self, project_id: int) -> list[ProjectMemberModel]:
        """Строго кураторы (без владельца)."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.role_project == "curator"
            )
        )
        return result.scalars().all()

    async def is_user_admin_or_curator(self, project_id: int, user_id: int) -> bool:
        """Владелец или куратор."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
                ProjectMemberModel.role_project.in_(['admin', 'curator'])
            )
        )
        return result.scalar_one_or_none() is not None

    async def is_user_admin(self, project_id: int, user_id: int) -> bool:
        """Проверка, является ли пользователь главой проекта."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
                ProjectMemberModel.role_project == 'admin'
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_user_projects(self, user_id: int) -> list[ProjectModel]:
        """Получить все проекты пользователя."""
        result = await self.session.execute(
            select(ProjectModel)
            .join(
                ProjectMemberModel,
                ProjectModel.project_id == ProjectMemberModel.project_id
            )
            .where(ProjectMemberModel.user_id == user_id)
        )
        return result.scalars().all()

    async def update_project_description(self, new_description: str, project_id: int) -> bool:
        """Обновление описание проекта."""
        result = await self.session.execute(
            update(ProjectModel)
            .values(project_description=new_description)
            .where(ProjectModel.project_id == project_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def update_project_name(self, new_name: str, project_id: int) -> bool:
        """Обновление названия проекта."""
        result = await self.session.execute(
            update(ProjectModel)
            .values(project_name=new_name)
            .where(ProjectModel.project_id == project_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def update_user_role(self, project_id: int, user_id: int, role: str) -> bool:
        """Обновление роли пользователя из проекта."""
        result = await self.session.execute(
            update(ProjectMemberModel)
            .values(role_project=role)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id
            )
        )
        await self.session.flush()
        return result.rowcount > 0

    async def delete_project(self, project_id: int) -> bool:
        """Удаление проекта."""
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
        await self.session.execute(
            delete(TaskCommentsModel).where(TaskCommentsModel.project_id == project_id)
        )
        result = await self.session.execute(
            delete(ProjectModel).where(ProjectModel.project_id == project_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def delete_user_from_project(self, project_id: int, user_id_to_del: int) -> bool:
        """Удаление пользователя из проекта."""
        result = await self.session.execute(
            delete(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id_to_del
            )
        )
        await self.session.flush()
        return result.rowcount > 0

    async def unassign_user_tasks_in_project(self, project_id: int, user_id: int) -> int:
        """Снимает assigned_to у всех задач пользователя проекта."""
        result = await self.session.execute(
            update(TaskModel)
            .where(
                TaskModel.project_id == project_id,
                TaskModel.assigned_to == user_id
            )
            .values(assigned_to=None)
        )
        await self.session.flush()
        return result.rowcount

    async def unassign_all_tasks_from_user(self, user_id: int) -> int:
        """Снимает assigned_to по всем проектам (перед удалением профиля)."""
        result = await self.session.execute(
            update(TaskModel)
            .where(TaskModel.assigned_to == user_id)
            .values(assigned_to=None)
        )
        await self.session.flush()
        return result.rowcount

    async def get_number_curators(self, project_id: int) -> int:
        """Получить количество кураторов проекта."""
        result = await self.session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.role_project == "curator"
            )
        )
        return result.scalar() or 0

    async def get_number_members(self, project_id: int) -> int:
        """Получить количество участников проекта."""
        result = await self.session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.role_project == 'member'
            )
        )
        return result.scalar() or 0