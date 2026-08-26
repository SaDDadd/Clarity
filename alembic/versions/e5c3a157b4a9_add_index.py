"""add_index

Revision ID: e5c3a157b4a9
Revises: cf26c315fc74
Create Date: 2026-08-26 14:42:43.655606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5c3a157b4a9'
down_revision: Union[str, Sequence[str], None] = 'cf26c315fc74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Индексы для таблицы tasks
    op.create_index('idx_tasks_task_status', 'tasks', ['task_status'])
    op.create_index('idx_tasks_deadline', 'tasks', ['deadline'])
    op.create_index('idx_tasks_project_status', 'tasks', ['project_id', 'task_status'])

    # Индекс для project_members
    op.create_index('idx_project_members_role', 'project_members', ['role_project'])

    # Индекс для project_invitations
    op.create_index('idx_invitations_status', 'project_invitations', ['status_invited'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_invitations_status', table_name='project_invitations')
    op.drop_index('idx_project_members_role', table_name='project_members')
    op.drop_index('idx_tasks_project_status', table_name='tasks')
    op.drop_index('idx_tasks_deadline', table_name='tasks')
    op.drop_index('idx_tasks_task_status', table_name='tasks')
