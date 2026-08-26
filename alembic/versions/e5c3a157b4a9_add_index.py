"""add missing indexes

Revision ID: 6f7a8b9c0d1e
Revises: e5c3a157b4a9
Create Date: 2026-08-27 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f7a8b9c0d1e'
down_revision: Union[str, Sequence[str], None] = 'e5c3a157b4a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Индексы для таблицы projects
    op.create_index('idx_projects_admin_id', 'projects', ['admin_id'])

    # Индексы для таблицы tasks
    op.create_index('idx_tasks_project_id', 'tasks', ['project_id'])
    op.create_index('idx_tasks_assigned_to', 'tasks', ['assigned_to'])
    op.create_index('idx_tasks_project_assigned', 'tasks', ['project_id', 'assigned_to'])

    # Индекс для таблицы project_members
    op.create_index('idx_project_members_role', 'project_members', ['role_project'])

    # Индексы для таблицы project_invitations
    op.create_index('idx_invitations_status', 'project_invitations', ['status_invited'])
    op.create_index('idx_invitations_project_status', 'project_invitations', ['project_id', 'status_invited'])
    op.create_index('idx_invitations_invitee_status', 'project_invitations', ['invitee_id', 'status_invited'])


def downgrade() -> None:
    # Удаление индексов (обратный порядок)
    op.drop_index('idx_invitations_invitee_status', table_name='project_invitations')
    op.drop_index('idx_invitations_project_status', table_name='project_invitations')
    op.drop_index('idx_invitations_status', table_name='project_invitations')

    op.drop_index('idx_project_members_role', table_name='project_members')

    op.drop_index('idx_tasks_project_assigned', table_name='tasks')
    op.drop_index('idx_tasks_assigned_to', table_name='tasks')
    op.drop_index('idx_tasks_project_id', table_name='tasks')

    op.drop_index('idx_projects_admin_id', table_name='projects')
