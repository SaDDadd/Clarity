"""init

Revision ID: 4ed2a0e57d1c
Revises:
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4ed2a0e57d1c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'projects',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('project_name', sa.String(length=100), nullable=False),
        sa.Column('project_description', sa.Text(), nullable=True),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('project_id'),
    )

    op.create_table(
        'project_members',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_project', sa.Enum('admin', 'member', name='role_project'),
                  server_default='member', nullable=False),
        sa.Column('joined_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('project_id', 'user_id'),
    )

    op.create_table(
        'tasks',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('task_description', sa.Text(), nullable=True),
        sa.Column('task_status', sa.Enum('pending', 'in_progress', 'completed', name='task_status'),
                  server_default='pending', nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('created_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.user_id']),
        sa.PrimaryKeyConstraint('task_id'),
    )

    op.create_table(
        'project_invitations',
        sa.Column('invitation_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('inviter_id', sa.Integer(), nullable=False),
        sa.Column('invitee_id', sa.Integer(), nullable=False),
        sa.Column('status_invited',
                  sa.Enum('pending', 'accepted', 'declined', name='invitation_status'),
                  nullable=True),
        sa.Column('created_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('update_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inviter_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['invitee_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('invitation_id'),
    )


def downgrade() -> None:
    op.drop_table('project_invitations')
    op.drop_table('tasks')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_table('users')